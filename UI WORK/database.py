"""
=============================================================================
             DATABASE REPOSITORY MODULE - JAINAGAR CHUNAV 2026
 High-performance SQLite database operations with sub-10ms query execution.
=============================================================================
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jainagar_chunav.db")


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def search_voters(self,
                      query: str = "",
                      ward: Optional[int] = None,
                      status: Optional[str] = None,
                      limit: int = 100,
                      offset: int = 0) -> List[Dict[str, Any]]:
        """
        Fast search across:
        - Voter Hindi Name
        - Voter English Name
        - EPIC / Voter ID (prefix & exact)
        - Serial No
        - House Number
        - Relative Name
        """
        query = query.strip()
        params: List[Any] = []
        conditions: List[str] = []

        if ward and ward > 0:
            conditions.append("ward_number = ?")
            params.append(ward)

        if status and status != "all":
            conditions.append("voter_status = ?")
            params.append(status)

        if query:
            # Check if query is numeric (serial no or house no)
            if query.isdigit():
                q_int = int(query)
                conditions.append("""(
                    serial_no = ? OR
                    house_number = ? OR
                    house_number LIKE ?
                )""")
                params.extend([q_int, query, f"{query}/%"])
            else:
                wildcard = f"%{query}%"
                prefix = f"{query.upper()}%"
                conditions.append("""(
                    epic_number LIKE ? OR
                    name_hindi LIKE ? OR
                    name_english LIKE ? OR
                    relative_hindi LIKE ? OR
                    relative_english LIKE ? OR
                    house_number LIKE ?
                )""")
                params.extend([prefix, wildcard, wildcard, wildcard, wildcard, wildcard])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"""
        SELECT
            id, ward_number, serial_no, epic_number,
            name_hindi, name_english,
            relative_type, relative_hindi, relative_english,
            house_number, age, gender_hindi, gender_english,
            section_name, panchayat_name, page_number,
            ocr_confidence, review_status, voter_status, karyakarta_notes
        FROM voters
        {where_clause}
        ORDER BY ward_number ASC, serial_no ASC
        LIMIT ? OFFSET ?;
        """
        params.extend([limit, offset])

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        results = [dict(r) for r in rows]
        conn.close()
        return results

    def get_voter_by_id(self, voter_id: int) -> Optional[Dict[str, Any]]:
        """Fetch single voter details by primary key."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM voters WHERE id = ?;", (voter_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_family_members(self, ward: int, house_number: str, exclude_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch all voters residing in the same house number in this ward."""
        if not house_number:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()
        if exclude_id:
            cursor.execute("""
            SELECT id, ward_number, serial_no, epic_number, name_hindi, name_english,
                   relative_type, relative_hindi, age, gender_english, voter_status
            FROM voters
            WHERE ward_number = ? AND house_number = ? AND id != ?
            ORDER BY serial_no ASC;
            """, (ward, house_number, exclude_id))
        else:
            cursor.execute("""
            SELECT id, ward_number, serial_no, epic_number, name_hindi, name_english,
                   relative_type, relative_hindi, age, gender_english, voter_status
            FROM voters
            WHERE ward_number = ? AND house_number = ?
            ORDER BY serial_no ASC;
            """, (ward, house_number))

        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_voter_status(self, voter_id: int, status: str, notes: str = "") -> bool:
        """Update election-day marking status (voted, supporter, doubtful, absent, unmarked)."""
        valid_statuses = ("unmarked", "voted", "supporter", "doubtful", "absent")
        if status not in valid_statuses:
            status = "unmarked"

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE voters
        SET voter_status = ?, karyakarta_notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?;
        """, (status, notes, voter_id))

        # Update ward polled count
        cursor.execute("""
        UPDATE ward_summary
        SET polled_count = (
            SELECT COUNT(*) FROM voters
            WHERE voters.ward_number = ward_summary.ward_number
            AND voters.voter_status = 'voted'
        );
        """)
        conn.commit()
        conn.close()
        return True

    def get_overall_stats(self) -> Dict[str, Any]:
        """Get aggregate campaign and voter statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            COUNT(*) as total_voters,
            SUM(CASE WHEN gender_english = 'Male' THEN 1 ELSE 0 END) as male_count,
            SUM(CASE WHEN gender_english = 'Female' THEN 1 ELSE 0 END) as female_count,
            SUM(CASE WHEN voter_status = 'voted' THEN 1 ELSE 0 END) as total_polled,
            SUM(CASE WHEN voter_status = 'supporter' THEN 1 ELSE 0 END) as total_supporters,
            SUM(CASE WHEN voter_status = 'doubtful' THEN 1 ELSE 0 END) as total_doubtful,
            SUM(CASE WHEN voter_status = 'absent' THEN 1 ELSE 0 END) as total_absent,
            AVG(CASE WHEN age > 0 THEN age ELSE NULL END) as avg_age
        FROM voters;
        """)
        row = dict(cursor.fetchone())

        # Age brackets
        cursor.execute("""
        SELECT
            SUM(CASE WHEN age BETWEEN 18 AND 25 THEN 1 ELSE 0 END) as youth_18_25,
            SUM(CASE WHEN age BETWEEN 26 AND 40 THEN 1 ELSE 0 END) as young_26_40,
            SUM(CASE WHEN age BETWEEN 41 AND 60 THEN 1 ELSE 0 END) as middle_41_60,
            SUM(CASE WHEN age > 60 THEN 1 ELSE 0 END) as senior_60_plus
        FROM voters;
        """)
        age_row = dict(cursor.fetchone())
        row.update(age_row)

        conn.close()
        return row

    def get_ward_summary(self) -> List[Dict[str, Any]]:
        """Get ward-by-ward breakdown with live polled turnout."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
            w.ward_number,
            w.total_voters,
            w.male_count,
            w.female_count,
            (SELECT COUNT(*) FROM voters v WHERE v.ward_number = w.ward_number AND v.voter_status = 'voted') as polled_count,
            (SELECT COUNT(*) FROM voters v WHERE v.ward_number = w.ward_number AND v.voter_status = 'supporter') as supporter_count
        FROM ward_summary w
        ORDER BY w.ward_number ASC;
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_candidate_profile(self) -> Dict[str, Any]:
        """Fetch Pradhyumna Nagar campaign profile."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidate_info WHERE id = 1;")
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
