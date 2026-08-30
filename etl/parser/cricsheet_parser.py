import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary. Returns default if obj is not a dict or key is missing."""
    if isinstance(obj, dict) and key in obj:
        return obj[key]
    return default


def safe_list(obj: Any) -> list:
    """Safely return a list. If obj is a list, returns obj. Otherwise returns an empty list."""
    if isinstance(obj, list):
        return obj
    return []


class CricsheetParser:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.current_match_id = None

    def log_error(self, message: str):
        self.errors.append({"match_id": self.current_match_id, "message": message})

    def log_warning(self, message: str):
        self.warnings.append({"match_id": self.current_match_id, "message": message})

    def parse_match(self, file_path: Path) -> Optional[Tuple[Dict, List[Dict], List[Dict]]]:
        """
        Parses a single Cricsheet JSON file.
        Returns (metadata_dict, list_of_batting_dicts, list_of_bowling_dicts) or None if parsing fails completely.
        """
        self.current_match_id = file_path.stem

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.log_error(f"Failed to load or parse JSON: {e}")
            return None

        info = safe_get(data, "info", {})
        innings_data = safe_list(safe_get(data, "innings", []))

        if not info or not innings_data:
            self.log_error("Missing mandatory 'info' or 'innings' objects.")
            return None

        try:
            metadata = self._extract_metadata(info)
            metadata["Match_ID"] = self.current_match_id

            batting_records = []
            bowling_records = []

            # Inning structure: [{"team": "...", "overs": [...]}, ...]
            for inning_index, inning in enumerate(innings_data):
                # Using 1-based inning numbers
                inning_num = inning_index + 1
                
                # Depending on the schema version, sometimes the team is under team or innings[0]['1st innings']['team']
                # But modern schema is innings: [{"team": "team", "overs": [...]}]
                # Let's handle the modern schema first (v1.0)
                team = safe_get(inning, "team", "")
                overs = safe_list(safe_get(inning, "overs", []))
                
                # Determine bowling team based on metadata if possible
                bowling_team = ""
                if team == metadata.get("Team_1"):
                    bowling_team = metadata.get("Team_2", "")
                elif team == metadata.get("Team_2"):
                    bowling_team = metadata.get("Team_1", "")
                
                batting, bowling = self._extract_inning_stats(overs, inning_num, team, bowling_team)
                
                for b in batting:
                    b["Match_ID"] = self.current_match_id
                    batting_records.append(b)
                
                for b in bowling:
                    b["Match_ID"] = self.current_match_id
                    bowling_records.append(b)
                    
            return metadata, batting_records, bowling_records
            
        except Exception as e:
            self.log_error(f"Unexpected error during extraction: {e}")
            return None

    def _extract_metadata(self, info: Dict) -> Dict:
        metadata = {}
        metadata["Format"] = safe_get(info, "match_type", "")
        
        dates = safe_list(safe_get(info, "dates", []))
        metadata["Match_Date"] = dates[0] if dates else ""
        
        # Handle teams: can be list or dict
        teams = safe_get(info, "teams")
        if isinstance(teams, list) and len(teams) >= 2:
            metadata["Team_1"] = teams[0]
            metadata["Team_2"] = teams[1]
        elif isinstance(teams, dict) and len(teams) >= 2:
            team_names = list(teams.keys())
            metadata["Team_1"] = team_names[0]
            metadata["Team_2"] = team_names[1]
        else:
            metadata["Team_1"] = ""
            metadata["Team_2"] = ""

        metadata["Venue"] = safe_get(info, "venue", "")
        
        toss = safe_get(info, "toss", {})
        toss_winner = safe_get(toss, "winner", "")
        toss_decision = safe_get(toss, "decision", "")
        if toss_winner and toss_decision:
            metadata["Toss"] = f"{toss_winner} chose to {toss_decision}"
        else:
            metadata["Toss"] = ""
            
        outcome = safe_get(info, "outcome", {})
        metadata["Result"] = safe_get(outcome, "result", "")
        
        player_of_match = safe_list(safe_get(info, "player_of_match", []))
        metadata["Player_of_the_Match"] = player_of_match[0] if player_of_match else ""
        
        return metadata

    def _extract_inning_stats(self, overs: List[Dict], inning_num: int, batting_team: str, bowling_team: str) -> Tuple[List[Dict], List[Dict]]:
        batting_stats = defaultdict(lambda: {"Runs": 0, "Balls": 0, "4s": 0, "6s": 0})
        
        # Bowling structure for maidens tracking:
        # {bowler: {"Overs_Bowled": 0, "Maidens": 0, "Runs_Conceded": 0, "Wickets": 0}}
        bowling_stats = defaultdict(lambda: {"Overs_Bowled": 0, "Maidens": 0, "Runs_Conceded": 0, "Wickets": 0})
        
        for over in overs:
            deliveries = safe_list(safe_get(over, "deliveries", []))
            
            # For maiden over tracking
            over_bowler = None
            runs_off_over = 0
            
            for delivery in deliveries:
                batter = safe_get(delivery, "batter")
                bowler = safe_get(delivery, "bowler")
                
                if not batter or not bowler:
                    continue
                    
                over_bowler = bowler
                
                runs_dict = safe_get(delivery, "runs", {})
                runs_batter = safe_get(runs_dict, "batter", 0)
                runs_extras = safe_get(runs_dict, "extras", 0)
                
                extras_dict = safe_get(delivery, "extras", {})
                
                # --- BATTING ---
                batting_stats[batter]["Runs"] += runs_batter
                
                if runs_batter == 4:
                    batting_stats[batter]["4s"] += 1
                elif runs_batter == 6:
                    batting_stats[batter]["6s"] += 1
                    
                # Exclude wides from balls faced
                if "wides" not in extras_dict:
                    batting_stats[batter]["Balls"] += 1
                    
                # Wickets mapping
                wickets = safe_list(safe_get(delivery, "wickets", []))
                for w in wickets:
                    player_out = safe_get(w, "player_out")
                    # If this delivery resulted in a wicket, we note it for the bowler
                    if player_out:
                        bowling_stats[bowler]["Wickets"] += 1

                # --- BOWLING ---
                bowling_stats[bowler]["Overs_Bowled"] += 1 # We accumulate total balls here, not overs yet
                runs_conceded = runs_batter + runs_extras
                bowling_stats[bowler]["Runs_Conceded"] += runs_conceded
                runs_off_over += runs_conceded

            # End of over: Maiden check
            if over_bowler and runs_off_over == 0 and len(deliveries) >= 6:
                bowling_stats[over_bowler]["Maidens"] += 1

        # Format Batting list
        batting_list = []
        for player, stats in batting_stats.items():
            bat_record = {
                "Player": player,
                "Innings": inning_num,
                "Team": batting_team,
                "Runs": stats["Runs"],
                "Balls": stats["Balls"],
                "4s": stats["4s"],
                "6s": stats["6s"]
            }
            batting_list.append(bat_record)
            
        # Format Bowling list
        bowling_list = []
        for player, stats in bowling_stats.items():
            overs = stats["Overs_Bowled"] // 6
            bowl_record = {
                "Player": player,
                "Innings": inning_num,
                "Team": bowling_team,
                "Overs": overs,
                "Maidens": stats["Maidens"],
                "Runs_Conceded": stats["Runs_Conceded"],
                "Wickets": stats["Wickets"],
                "Balls_Bowled": stats["Overs_Bowled"]
            }
            bowling_list.append(bowl_record)
            
        return batting_list, bowling_list
