from collections import defaultdict
from app import get_professors
import os
import datetime

swap_file = os.path.join(os.path.dirname(__file__), "section_swaps.txt")

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
    couldnt_find_swap = []

    for slot, classes in slots.items():
        overfull = [c for c in classes if c["enrollment"] > c["capacity"]]

        # if no classes in this specific timeslot are full capacity
        # then we don't need to do anything 
        # and can skip to the next timeslot
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
                    "crowded_class_name": crowded["course_num"],
                    "target_id":      target["id"],
                    "target_room":    target["room"],
                    "target_class_name": target["course_num"],
                    "reason": (f"{crowded['enrollment']} students need "
                            f"{target['capacity']}-seat room")
                })

                log_swap = (
                    f"\n{datetime.datetime.now():%Y-%m-%d %H:%M:%S}  "
                    f"{slot}:  "
                    f"{crowded['course_num']} ({crowded['room']}) -> "
                    f"{target['course_num']} ({target['room']})\n"
                    )
                
                with open(swap_file, "a") as logfile:
                    logfile.write(log_swap)

                used_target.add(target["id"])
                spare_sorted.remove(target)
            else:
                # add the crowded class that failed to find a swap
                # to the find swap list so we can try to find a swap
                # in another timeslot
                couldnt_find_swap.append({
                    "id": crowded["id"],
                    "course_num": crowded["course_num"],
                    "room": crowded["room"],
                    "enrollment": crowded["enrollment"],
                    "capacity": crowded["capacity"],
                    "slot": slot
                })

        if slot_recs:
            recommendations[slot] = slot_recs

    return recommendations, couldnt_find_swap

def recommended_swaps_if_no_swaps_in_same_timeslot(db_path, not_swappable):
    """
    Try to place still-crowded classes into another slot/room.
    A move is legal only if the crowded class's professor is free
    in the target slot AND the target professor stays conflict-free.
    """

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.room, c.meeting_pattern,
            c.enrollment, c.max_enrollment, c.course_number,
            p.id                 AS professor_id
            FROM   classes            c
            JOIN   class_professors   cp ON cp.class_id = c.id
            JOIN   professors         p  ON p.id = cp.professor_id
        """)
        rows = cur.fetchall()

    # create dicts to hold class data
    # and professor schedules
    # and a list of classes in each slot
    classes      = {}                         
    class_prof   = {}                        
    prof_busy    = defaultdict(set)           
    slots        = defaultdict(list)          
    
    for r in rows:
        c = {
            "id":       r[0],
            "room":     r[1],
            "slot":     r[2],
            "enroll":   r[3],
            "cap":      r[4],
            "prof_id":  r[6],
            "course_num": r[5]
        }
        classes[c["id"]] = c
        class_prof[c["id"]] = c["prof_id"]
        prof_busy[c["prof_id"]].add(c["slot"])
        slots[c["slot"]].append(c)

    # remove classes that are already in a swap
    # and classes that are not over capacity
    recommendations = defaultdict(list)

    for crowded in not_swappable:
        c = classes[crowded["id"]]
        c_prof = c["prof_id"]

        for slot, candidates in slots.items():
            if slot == c["slot"]:
                continue                     # must be different slot
            if slot in prof_busy[c_prof]:
                continue                     # professor already busy

            # candidate class / room large enough?
            target = next((t for t in candidates
                        if t["cap"] >= c["enroll"]
                        and t["room"] != c["room"]
                        and (t["slot"] not in prof_busy[c_prof])
                        and (c["slot"] not in prof_busy[t["prof_id"]])
                        ), None)

            if target:
                recommendations[slot].append({
                    "old_slot":       c["slot"],
                    "new_slot":       slot,
                    "crowded_id":     c["id"],
                    "crowded_room":   c["room"],
                    "crowded_class_name": c["course_num"],
                    "target_class_name": target["course_num"],
                    "target_id":      target["id"],
                    "target_room":    target["room"],
                    "reason": (f"{c['enroll']} students need {target['cap']}-seat "
                    f"room; professor {c_prof} free at {slot}")
                })

                log_swap = (
                    f"\n{datetime.datetime.now():%Y-%m-%d %H:%M:%S}  "
                    f"{slot}:  "
                    f"{crowded['course_num']} ({crowded['room']}) -> "
                    f"{target['course_num']} ({target['room']})\n"
                    )
                
                with open(swap_file, "a") as logfile:
                    logfile.write(log_swap)

                # update professor schedules so later moves respect this swap
                prof_busy[c_prof].add(slot)
                break                      

    return dict(recommendations)


if __name__ == "__main__":
    import sqlite3
    import os

    DB_FILE = "database.db"

    # Find same slot swaps first to avoid unnecessary cross-slot swaps
    same, not_swappable = recommend_swaps_per_timeslot(DB_FILE)

    if same:
        print("\n=== SAME-SLOT RECOMMENDATIONS ===")
        for slot in sorted(same):                          # keep order tidy
            print(f"{slot}:")
            for rec in same[slot]:
                print(f"  • {rec['crowded_class_name']} ({rec['crowded_room']})  →  "
                    f"{rec['target_class_name']} ({rec['target_room']})")
    else:
        print("\nNo same-slot swaps found.")

    # Secondly try to find cross-slot swaps for classes that couldn't be moved
    # in the same slot
    if not_swappable:
        print("\n=== STILL OVER CAPACITY ===")
        for c in not_swappable:
            print(f"  • {c['course_num']} in {c['room']} "
                f"({c['enrollment']}/{c['capacity']}) at {c['slot']}")
    else:
        print("\nNo classes left over capacity.")

    cross = recommended_swaps_if_no_swaps_in_same_timeslot(DB_FILE, not_swappable)

    if cross:
        print("\n=== CROSS-SLOT RECOMMENDATIONS ===")
        for slot in sorted(cross):
            print(f"{slot}:")
            for rec in cross[slot]:
                print(f"  • {rec['crowded_class_name']} ({rec['crowded_room']})  →  "
                    f"{rec['target_class_name']} ({rec['target_room']})")
    else:
        print("\nNo cross-slot swaps needed.")

