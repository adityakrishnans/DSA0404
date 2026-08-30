import time
from pathlib import Path

from config.settings import SOURCE_JSON_DIR, DATASET_PATH
from etl.parser.cricsheet_parser import CricsheetParser
from etl.transformer.fact_table_builder import build_fact_table
from etl.validator.dataset_validator import DatasetValidator


class ETLPipeline:
    def __init__(self, source_dir: Path = SOURCE_JSON_DIR, output_path: Path = DATASET_PATH):
        self.source_dir = source_dir
        self.output_path = output_path
        self.parser = CricsheetParser()
        self.validator = DatasetValidator()

    def _discover(self) -> list[Path]:
        """Locates and sorts all JSON files in the source directory."""
        if not self.source_dir.exists():
            print(f"[Discovery] Source directory does not exist: {self.source_dir}")
            return []
        
        files = sorted(self.source_dir.glob("*.json"))
        print(f"[Discovery] Found {len(files)} JSON files in {self.source_dir}")
        return files

    def run(self):
        """Executes the full ETL pipeline."""
        start_time = time.time()
        print("[Pipeline] Starting ETL pipeline...")

        # 1. Discovery
        files = self._discover()
        if not files:
            print("[Pipeline] No files to process. Exiting.")
            return

        # 2 & 3. JSON Loading & Parsing
        all_metadata = []
        all_batting = []
        all_bowling = []
        
        successful_files = 0
        skipped_files = 0

        print(f"[Parser] Beginning extraction of {len(files)} files...")
        
        for i, file_path in enumerate(files, 1):
            if i % 500 == 0:
                print(f"[Parser] Processed {i} files...")
                
            parsed_data = self.parser.parse_match(file_path)
            
            if parsed_data is None:
                skipped_files += 1
                continue
                
            metadata, batting, bowling = parsed_data
            all_metadata.append(metadata)
            all_batting.extend(batting)
            all_bowling.extend(bowling)
            successful_files += 1

        print(f"[Parser] Extraction complete. {successful_files} parsed, {skipped_files} skipped.")

        # 4 & 5. Aggregation & Transformation
        print("[Transformer] Building fact table DataFrame...")
        try:
            df = build_fact_table(all_metadata, all_batting, all_bowling)
        except Exception as e:
            raise RuntimeError(f"Transformation failed: {e}") from e

        print(f"[Transformer] DataFrame constructed with shape: {df.shape}")

        # 6. Validation
        print("[Validator] Running dataset validation checks...")
        validation_result = self.validator.validate(df)
        
        if not validation_result.passed:
            validation_result.log_failures()
            raise RuntimeError("Validation failed. Check the logs above for details.")
        print("[Validator] All validation checks passed successfully.")

        # 7. Export
        print(f"[Export] Writing to {self.output_path}...")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_path, index=False)
        
        file_size_mb = self.output_path.stat().st_size / (1024 * 1024)
        print(f"[Export] Success. Exported size: {file_size_mb:.2f} MB")

        elapsed_time = time.time() - start_time
        
        # Summary execution report requested by the user
        print("-" * 40)
        print("ETL EXECUTION SUMMARY")
        print("-" * 40)
        print(f"Total files processed : {len(files)}")
        print(f"Successful files      : {successful_files}")
        print(f"Failed/skipped files  : {skipped_files}")
        print(f"Exported rows         : {len(df)}")
        print(f"Exported columns      : {len(df.columns)}")
        print(f"Elapsed time          : {elapsed_time:.2f} seconds")
        print("-" * 40)


if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run()
