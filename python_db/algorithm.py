from collections import defaultdict

def recommend_swaps_per_timeslot(db_path):
    """
    This function will read the SQLite database, fetch all classes, and recommend swaps for each timeslot.
    For example if a specific timeslot within PKI has 1-2 classes that are full capacity it will try to 
    find a class that is not full capacity and suggest a swap. It will need to continue to do this until
    all classes enrollments are below the maximum capacity (unless its impossible to do so).
    """

    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()
    cur.execute("""
        SELECT id, course_number, room,
            meeting_pattern,
            enrollment, max_enrollment
        FROM classes
    """)
    rows = cur.fetchall()
    conn.close()

    # group classes by meeting pattern (timeslot)
    slots = defaultdict(list)
    for r in rows:
        slots[r[3]].append({
            "id":         r[0],
            "course_num": r[1],
            "room":       r[2],
            "enrollment": r[4],
            "capacity":   r[5]
        })

    recommendations = {}

    for slot, classes in slots.items():
        overfull = [c for c in classes if c["enrollment"] > c["capacity"]]
        if not overfull:
            continue                               

        # rooms sorted by spare seats DESC
        spare_sorted = sorted(
            classes,
            key=lambda c: c["capacity"] - c["enrollment"],
            reverse=True
        )

        slot_recs   = []
        used_target = set()                       

        for crowded in sorted(overfull,
                            key=lambda c: c["enrollment"],
                            reverse=True):

            target = next(
                (
                    r for r in spare_sorted
                    if r["room"] != crowded["room"]      
                    and r["capacity"] >= crowded["enrollment"]
                    and r["id"] not in used_target
                ),
                None
            )

            if target:
                slot_recs.append({
                    "crowded_id":     crowded["id"],
                    "crowded_room":   crowded["room"],
                    "target_id":      target["id"],
                    "target_room":    target["room"],
                    "reason": (f"{crowded['enrollment']} students need "
                            f"{target['capacity']}-seat room")
                })
                used_target.add(target["id"])
                spare_sorted.remove(target)

        if slot_recs:
            recommendations[slot] = slot_recs

    return recommendations

if __name__ == "__main__":
    import sqlite3
    import os

    DB_FILE = "database.db"
    recommendations = recommend_swaps_per_timeslot(DB_FILE)

    for slot, recs in recommendations.items():
        print(f"Recommendations for {slot}:")
        for rec in recs:
            print(f"  Swap {rec['crowded_room']} with {rec['target_room']}")
        print()
    print("No recommendations found.")
