import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from config.settings import (
    SCHEMA_COLUMNS,
    PRIMARY_KEY,
    METADATA_COLS,
    VALID_FORMATS,
    VALID_INNINGS,
    VALID_ROLES
)


@dataclass
class CheckResult:
    check_name: str
    passed: bool
    message: str = ""


@dataclass
class ValidationResult:
    checks: List[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def log_failures(self):
        for check in self.checks:
            if not check.passed:
                print(f"FAILED CHECK: {check.check_name} - {check.message}")


class DatasetValidator:
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        result = ValidationResult()
        
        result.checks.append(self._check_column_schema(df))
        result.checks.append(self._check_row_counts(df))
        result.checks.append(self._check_duplicate_primary_keys(df))
        result.checks.append(self._check_metadata_completeness(df))
        result.checks.append(self._check_format_values(df))
        result.checks.append(self._check_innings_values(df))
        result.checks.append(self._check_role_values(df))
        result.checks.append(self._check_role_stat_consistency(df))
        result.checks.append(self._check_numeric_sanity(df))
        
        return result

    def _check_column_schema(self, df: pd.DataFrame) -> CheckResult:
        actual_cols = list(df.columns)
        if actual_cols == SCHEMA_COLUMNS:
            return CheckResult("Column schema", True)
        return CheckResult("Column schema", False, f"Mismatch. Expected {SCHEMA_COLUMNS}, got {actual_cols}")

    def _check_row_counts(self, df: pd.DataFrame) -> CheckResult:
        if len(df) > 0:
            return CheckResult("Row counts", True)
        return CheckResult("Row counts", False, "Dataset is empty")

    def _check_duplicate_primary_keys(self, df: pd.DataFrame) -> CheckResult:
        duplicates = df.duplicated(subset=list(PRIMARY_KEY), keep=False)
        if not duplicates.any():
            return CheckResult("Duplicate primary keys", True)
        return CheckResult("Duplicate primary keys", False, f"Found {duplicates.sum()} duplicate rows")

    def _check_metadata_completeness(self, df: pd.DataFrame) -> CheckResult:
        mandatory = ["Match_ID", "Format", "Match_Date", "Team_1", "Team_2", "Venue"]
        for col in mandatory:
            missing = df[col].isna().sum() + (df[col] == "").sum()
            if missing > 0:
                return CheckResult("Metadata completeness", False, f"Column '{col}' has {missing} blank/missing values")
        return CheckResult("Metadata completeness", True)

    def _check_format_values(self, df: pd.DataFrame) -> CheckResult:
        invalid = df[~df["Format"].isin(VALID_FORMATS) & (df["Format"] != "")]
        if invalid.empty:
            return CheckResult("Format values", True)
        return CheckResult("Format values", False, f"Found invalid formats: {invalid['Format'].unique()}")

    def _check_innings_values(self, df: pd.DataFrame) -> CheckResult:
        invalid = df[~df["Innings"].isin(VALID_INNINGS) & df["Innings"].notna()]
        if invalid.empty:
            return CheckResult("Innings values", True)
        return CheckResult("Innings values", False, f"Found out-of-range innings: {invalid['Innings'].unique()}")

    def _check_role_values(self, df: pd.DataFrame) -> CheckResult:
        valid_with_blank = VALID_ROLES.union({""})
        invalid = df[~df["Role"].isin(valid_with_blank)]
        if invalid.empty:
            return CheckResult("Role values", True)
        return CheckResult("Role values", False, f"Found unrecognised roles: {invalid['Role'].unique()}")

    def _check_role_stat_consistency(self, df: pd.DataFrame) -> CheckResult:
        # Batters must have non-blank Runs
        batters_invalid = df[(df["Role"] == "Batter") & df["Runs"].isna()]
        # Bowlers must have non-blank Overs
        bowlers_invalid = df[(df["Role"] == "Bowler") & df["Overs"].isna()]
        
        if batters_invalid.empty and bowlers_invalid.empty:
            return CheckResult("Role-stat consistency", True)
            
        return CheckResult("Role-stat consistency", False, "Found batters with blank runs or bowlers with blank overs")

    def _check_numeric_sanity(self, df: pd.DataFrame) -> CheckResult:
        for col in ["Strike_Rate", "Economy", "Runs", "Wickets"]:
            if col in df.columns:
                negative = df[df[col] < 0]
                if not negative.empty:
                    return CheckResult("Numeric sanity", False, f"Column {col} has negative values")
        return CheckResult("Numeric sanity", True)
