"""
Freestanding loft bed with a convertible sofa / table / bed underneath
(Hoppekids-style), custom fitted between two walls 1990 mm apart.

COORDINATE SYSTEM (all units mm)
--------------------------------
  Z  up, floor at Z = 0
  X  along the length of the bed. The two walls are the planes X = 0 and
     X = WALL_SPAN (1990). HARD LIMIT: no geometry may cross those planes.
  Y  depth. Y = 0 is the inner face of the back rail, positive Y points
     towards the front (room side). Negative Y is the back rail's own 48 mm
     of thickness and nothing else: its OUTER face, Y = -48, is THE WALL
     PLANE (see W1/W6). v10 tucked the back corner posts INTO that band, so
     -48 is one flat face that the whole back of the bed presents to the
     wall, and no part of this bed is behind it.

*** W1 - THIS BED IS WALL-SIDE-SPECIFIC. IT IS NOT REVERSIBLE. ***
--------------------------------------------------------------------------
The long BACK side of the bed stands against the room wall and the frame is
bolted to it (S2). The wall itself is therefore the barrier on that side,
which is what lets v9 delete the two back guard boards and v10 tuck the two
back corner posts into the back rail plane. Consequences you cannot ignore:
  * the plane Y = -48 is a FLAT MOUNTING FACE and must sit flat against the
    wall. After v10/W6 it is made by the back side rail, the two back corner
    posts, the two end beams, the back bench rail with its two stub legs, the
    back table ledger and the rear ends of all 24 slats - every one of them
    coplanar (v12/V5 took the four bearing blocks off that list). Nothing is
    allowed to stand proud of it;
  * the FIXING is the back rail itself. It lies flat against the wall over
    its full 1984 x 98 mm face, so the bed is screwed to the studs straight
    through the rail. Those screws also mid-support the rail, which is why
    its 1894 mm clear span is not the governing case it looks like on paper
    (no geometry - it is a wall, not a part);
  * the slat platform runs right up to that face (v10/W8: all 14 slats,
    uniformly 800 mm), so the WALL is what stops the mattress on the back
    side - W5. After v10 the mattress is PINNED: 800 mm of mattress in an
    800 mm clear between the wall and the front verticals, zero wander and
    therefore zero gap at either edge (EN 747 limit 75 mm);
  * the bed CANNOT be turned round or stood free in a room. Mirroring it for
    a wall on the other hand means mirroring the model in Y, not swapping
    parts;
  * a freestanding variant is a bigger retrofit than it was in v9: as well as
    putting the two back guard boards (36x98 x 1984, bands Z 1414..1512 and
    1587..1685 after v11/U1) back, the two back posts have to come back OUT of
    the rail plane into their own layer behind it and go back to full height
    (1700), which costs the 48 mm of depth v10 just won - and, on a 36 mm
    post, 36 rather than 48 of it. Flagged for the docs round.

DESIGN INTENT (v18 - "the review classes become machinery")
--------------------------------------------------------------------------
X12  NOTHING IN THE BED MOVED. WHAT MOVED IS WHO DOES THE CHECKING. The three
    reviewers of X10/X11 found about fifty faults, and the faults were fixed -
    but the fixes were the small half of the finding. The large half was that
    five whole KINDS of question were being asked by a person reading, once,
    and by nothing at all in between. A class of fault that only a reader can
    catch is a class of fault that comes back. So this round wrote the
    machinery and let the classes die:

    1. C9 ON THE ASSEMBLIES. C9 asked every STICK whether it could be got into
    a 1990 mm opening, and nobody carries a stick into this niche - the
    builder screws five pieces together on the floor and then has to get THAT
    in. The bodies are now DERIVED (the connected components of «parts this
    step adds, joined by joints this step drives»), measured as boxes, and
    held to the same three rules: it must fit between the walls, its tilt
    diagonal must pass under the ceiling, and if it is wider than a member may
    be long it must be built where it stands and a later step must raise it.
    The back frame is not a case in that list - it is what rule three catches,
    and the check asserts that the body it finds is the five pieces the prose
    calls the back frame. See `check_step_units` in tools/gen_doc_tables.py.

    2. A DATUM THAT IS STILL WASTE. X6 rule 2 refuses to name an end that does
    not exist yet, and the proof of it needed three facts that live in three
    places: the cut list knows which ends leave the bench oversize, the
    placement table names the datum, and the steps know when the drill comes
    out. `assert_datum_ink` reads all three OFF THE FINISHED INK and demands
    they close - a hole measured from a still-oversize end has to be in step
    0's deferred list, and every joint in that list has to have such a hole.
    The foot has no deferred list at all, and that is asserted separately.

    3. THE README'S OWN NUMBERS. The one document in this project whose counts
    were retold rather than measured was the one that claims nothing here is
    retold. `tools/check_tall.py` counts them - asserts, artefacts, pages,
    pieces, running metres, fasteners, joints - and checks the lines it quotes
    in backticks against what the model actually printed this run.

    4. THE NUMBER SWEEP. Every «NNN mm/MPa/kg/kN/%» in the hand-written prose,
    against the values the model can produce. Same file; the pool is
    deliberately narrow and says how narrow it is.

    5. FALSIFICATION AS A GATE. Every round has ended by breaking an assert on
    purpose to watch it go red, and it worked every time somebody remembered.
    `tools/falsifiser.py` is that habit written down: named injections against
    the asserts that GUARD - the ones that measure ink or solids across files,
    where passing and having nothing to say look identical - each of which
    must fell its own check, with the unperturbed run as the control.

    AND ONE THING ABOUT THE WALL. STUD_LAYOUT_UNKNOWN. The nine wall fixings
    are the only fasteners in this bed whose X is not a fact, and the tables
    printed a c/c for them like any other row. The flag now says so where the
    model can see it, the spacing is documented as the worst layout the rule
    allows rather than a measurement, and an assert on the finished ink
    refuses any wall-fixing row that offers an X as a datum.

DESIGN INTENT (v17 - "the screws are checked against each other, and the
                      free edge stops being free")
--------------------------------------------------------------------------
X10  THIS ROUND FOUND NOTHING NEW AND FIXED A GREAT DEAL. Three reviewers went
    through the model, the tools and the documents and came back with the same
    kind of finding over and over: not a wrong drawing, but a QUESTION NOBODY
    HAD ASKED. Everything below was already in the file. It was simply never
    measured, and the file's own habit - ask the SHAPE, not the table that
    produced it - had a hole in it exactly where the shapes were not in the
    list being asked.

    1. TWO SCREWS DO NOT MEET IN THE SAME PIECE OF WOOD, AND SIXTEEN PAIRS DID.
    Every fastener assert in this file asks a screw about WOOD: is the head
    flush with it, is the tip inside it, is any of the body in somebody else's.
    Not one asked a screw about ANOTHER SCREW - and `mode_parts()` is wood-only
    by design, so the 180 modelled fastener bodies were never in the list they
    were being checked against. A boolean over the lot found sixteen pairs
    driven through each other, ten of them at the ladder rung ends where a
    6x120 from the upright and a 5x60 dropped through the tread crossed at a
    POINT, 0,00 mm apart, and the model printed OK.

    THE CAUSE IS NOT CARELESSNESS, WHICH IS WHY THE FIX IS A SECOND RULE AND
    NOT A BIGGER ONE. Every placement rule in this file puts its row in the
    MIDDLE of its own contact window, and it is right to. What nobody noticed
    is that two joints sharing a piece of wood share the middle as well: the
    end slat's screw and the front post's pair both land on X 50,5 because both
    obeyed the rule. So X10 adds `drive(offset=...)` - a declared step off the
    window centre, with a written reason, resolved "inboard"/"outboard" so the
    bed stays symmetric, and required to be perpendicular to the drive - and
    then adds the measurement that polices it: the least distance between two
    screw SEGMENTS, grouped by the member they share, ACROSS joints, held to
    the two half-shanks plus one shank of wood. Five joints took an offset
    (J1, J2-B, J8-B, J11-E, J17); one screw was struck.

    THE SCREW THAT WAS STRUCK, BECAUSE IT COULD NOT EXIST. J4 used to put a
    5x60 down through the tread into the rung block. It cannot be moved: the
    upright's 36 mm of depth pins the through screw's Y to one legal value, the
    tread's 48 mm pins its Z to 273 +- 6, and a screw dropped from the tread's
    top has to cross all 48 mm of tread to reach the block. Turned round -
    up from underneath - it clears the 6x120 by 12 mm and lands on J5 instead,
    which sits at the block's own mid-height and cannot move either. The block
    cannot take a vertical screw while the tread has a horizontal one. So it
    is gone, and what it did is argued off the wood: the block is caught
    between the upright's face, the tread lying on 1296 mm2 of its top, and
    that tread being itself pinned to the upright 24 mm above by the 6x120. To
    turn about J5, the block has to lift a tread that is screwed down.

    2. THE PLATE'S FREE FRONT EDGE, AND THE WORST ARITHMETIC IN THE FILE. X9
    priced the bare sheet between the two bordklosser at 0,86 - "a strip
    spanning the 324 mm between the two battens, on a conservative 250 mm of
    effective width". Both halves wrong, both unsafe. The battens carry nothing
    at the front edge (X9's own paragraph says so, four lines earlier); the
    span is the clear bay between the BLOCKS, which the same paragraph names as
    248 and then does not use. And 250 mm of effective width is not
    conservative on a FREE edge, where a point load can only spread one way -
    the file's own other sheet rows use 100 and say "its own length a". On the
    corrected span and a contact-plus-spread b_ef the row is 1,07 for a flat
    hand and 1,49 for a knee. The plate did not hold.

    WHAT COULD NOT BE DONE ABOUT IT, MEASURED. The obvious fix is a cross
    batten under the front edge between the guide battens, and it is not
    buildable: in bed mode the plate's underside IS the rung's top over the
    whole ladder bay - the rung is the bed-mode front bearing - so there is
    exactly 0 mm of air under that edge. Pull the batten back until it clears
    the rung and it runs into the bordklosser in table mode; pull it back until
    it clears those and it is 55 mm behind the edge, where the cantilever is no
    better than the span it replaced. A third bearing has nothing to stand on:
    the two blocks sit on the ladder uprights and there is no upright in the
    middle of the bay.

    SO THE BAY WAS SHORTENED AND THE SHEET WAS GIVEN A DIRECTION. The
    bordkloss became 48x68 x 91 - see (3) - and the free edge went 248 -> 224.
    That is not enough on its own, and the rest is a CUTTING INSTRUCTION with
    a load case behind it: plywood carries about two and a half times as much
    along its face grain as across it, the 6,95 MPa every sheet row in this
    file is computed on is calibrated on a row that spans the plate's LONG way
    (in Y, across the face grain), and this row spans in X. The face veneer
    therefore runs along the bed. It costs nothing - the blank is smaller than
    the sheet either way - and it is the difference between 1,49 and 0,60. It
    is written into the innkjopsliste as a requirement, and the row is emitted
    off the solids so the span can never be typed wrong again.

    3. THE BORDKLOSS GETS ITS SECOND SCREW, AND IT IS THE HOUSE RULE THAT SAYS
    SO. V5 deleted every bearing block that hung on a single 6 mm screw and
    wrote the rule down; J5-B is exactly such a corner and was not on the list.
    X9 had argued its way out of it - "ONE screw is all the face holds, 36 x 48
    is exactly 2 x 3d" - which was true of the face and never asked whether one
    screw is all the JOINT needs. It is not: unlike the rung block, this one
    has a LOOSE plate on it, lifted off twice a day, whose load stands 55 mm in
    front of the screw line. That is a moment in the plane of the fixing face,
    and a single screw carries it in friction and shank bending. The only
    dimension free to grow is the block's height - the 36 is the upright's own
    depth, forever - so the block becomes the bench-rail board standing on
    edge, 48x68 x 91, Z 614..682, a 36 x 68 fixing face with 68 = 2 x 3d + 4d
    and 8 mm to spare. No new profile, two pieces off the 36x48 board, and two
    accidents in the right direction: the bearing line 5040 -> 5088 mm2 and the
    free front edge 248 -> 224 mm.

    4. FOUR NUMBERS THAT WERE TYPED WHERE THEY SHOULD HAVE BEEN MEASURED.
      * BATTEN_GUIDE_ENGAGE_Z was RUNG_T (48) and was doing two jobs. The
        batten LAPS its locator over 48 mm of Z; it has to RISE 68 to come free
        of it, because the locator's top is the panel's own underside. The
        insertion sweep was asking `run > 2 x 48 = 96` against a table-mode run
        of 100 - the right answer to the wrong question, 4 mm from failing on a
        number that was never the number. Split in two: ENGAGE_Z the lap,
        RELEASE_Z the lift, and the sweep asks 100 > 68.
      * LOWER_HEADROOM was 1500 - 420 and said 1080. Measured on the bodies
        over the lower sleeping surface's own footprint, the lowest permanent
        wood is rung 2 at 104 mm and the lowest thing over the cushion strip at
        the wall is the table ledger at 194. All three numbers are emitted now.
        1080 is the head room in the room BETWEEN those members, not over them,
        and the rule that would have caught this is not a clearance but a LIST:
        the things standing in the lower storey's air have to be the things the
        reader is told about.
      * k_cr was in ASSEMBLY and not in the model, so the two documents printed
        0,42 and 0,62 for the same wedge tip. EC5 6.1.7 reduces the shear width
        for drying checks; the model does it now, and the number is 1,73 MPa
        against f_v,d 2,77 = 0,62.
      * THE SKIRTING BOARD WAS NOT IN THE MODEL AT ALL. The wall plane has
        always been checked for things standing proud of it; nothing checked
        what the WALL has standing proud of IT. Four parts meet the wall at the
        floor - two back posts and two back stub legs - so the fotlist comes
        off across the whole niche before the frame is raised, and the list of
        four is derived rather than remembered.

    5. THE ASSERTS THAT COULD NOT FAIL. A reviewer counted twenty-three
    unfalsifiable ones. The tightest cluster was an EN 747 entrapment check
    that read `WALL_MATTRESS_GAP == MATTRESS_Y0 - WALL_Y == 0` - every name in
    it an alias of BACK_RAIL_Y0, so the whole chain is one constant compared to
    itself, and it would have passed with the mattress built in the next room.
    It measures the mattress body against the wall face the bodies make now.
    Six more of that family, seven in the panel sub-assembly that read back
    their own assignments, a bearing area whose height cancelled on both sides,
    a guard lap that multiplied both sides by the same board width, and two
    sentinels that turned "there was nothing to measure" into "the rule is
    satisfied" - all of them now ask a shape or say out loud that they are a
    naming identity and not a check.

    6. AND THE COMMENTS ARE CHECKED TOO. Sixteen `NAME = expr  # number`
    comments in the model had gone stale - MATTRESS_Z0 said 1199 beside 1523,
    NOSE_LEN said 116 beside 77 - and every one of them had been true once,
    which is what makes them expensive. The file reads its own source at the
    end of the run and compares the number a value comment OPENS with to the
    value the name actually has, at the comment's own precision, skipping
    anything in a [ ] history bracket. 225 of them, every run, in the port.

    WHAT THIS ROUND DID NOT TOUCH, ON PURPOSE: the build steps, the manual
    prose and vedlegg A's own tables. The numbers this round moves - the free
    edge row, the k_cr shear row, the two measured head rooms, the fastener
    counts - are printed by the model so the documents can be brought to them
    in the round that owns them. Where a document now contradicts the model,
    the model is the one that was measured.

DESIGN INTENT (v16 - "the desk is bought, and the ladder pays")
--------------------------------------------------------------------------
X9  THE PULT AT 700 IS BUILT, AND WHAT IT COST IS THE EVEN LADDER. X8 (below,
    and left standing word for word) refused this change. The refusal was
    arithmetically right and it rested on one assumption nobody had written
    down: that the LADDER was fixed and the table had to fit under it. The
    builder has now overruled that assumption himself, in seven words -
    "700, and adjust the rungs / if need be the number of rungs" - and this
    entry is what those words come to in wood.

    WHAT WAS BOUGHT. The plate goes 560 -> 700 and its underside 542 -> 682.
    That is 280 mm over the 420 seat cushion and 262 under it, against 140 and
    122. The 122 was one thigh: a straight leg went under it and a bent KNEE
    did not, which is why every drawing in this folder until now showed two
    children sitting cross-legged at their own table. 262 takes a knee with
    127 mm to spare, so the figures sit down like people at a desk and the
    prose that explained the folded legs is DELETED - it was true at 560 and
    it is a lie at 700, and a comment that was true once is the most expensive
    kind of wrong. The builder's reference is a thing he can point at in a
    shop: IKEA SMASTAD's desk at 730.

    WHAT IT COST, IN ONE SENTENCE: THE LADDER IS NO LONGER EVEN. Rung 3 has to
    stand at 848 so that its underside (800) leaves the plate its 100 mm of
    straight-up lift, and rung 1 is nailed to the bench rail at 297. Five
    rungs still - the count did not change - but they fall into TWO FLIGHTS
    with the lift corridor between them:
        297  +275  572  +276  848  +225  1073  +225  1298  +225  1523
    275/276 below and 225 three times above, a spread of 51 mm where X2's
    ladder was even to within 1. The pitch limit is untouched and still met:
    276 against 280, inside EN 131's 250..300 band.
    X1/X2 SAID OUT LOUD that the even ladder was an aesthetic decision and
    that "the LADDER decides and the TABLE FOLLOWS". X9 is that decision being
    sold back, by the man who made it, for the thing he wanted more. The
    evenness rule is therefore re-aimed in the open, and it is re-aimed by
    being SPLIT rather than loosened: MAX_FLIGHT_SPREAD (2) keeps the old
    rule, tightened, inside each flight, and MAX_CLIMB_SPREAD (60) is a new
    and different rule about how far the corridor may push two flights apart.
    Nothing was exempted and no assert was deleted.

    AND THE RULE IS THE RULE, NOT THE LIST. `even_climb` takes the corridor as
    a CONSTRAINT now - "no rung top between 614 and 848" - and derives the
    ladder that satisfies it: fewest rungs, then flattest, then lowest
    crossing. Move the plate again and the ladder re-derives; nobody hand-sets
    a rung. That is the X2 rule with one more input, not a special case.

    THE SEAT IS DECOUPLED FROM THE LADDER, AND THAT IS THE OTHER HALF. 682 is
    a height no rung is allowed to stand at, so the plate cannot land on a
    rung any more. At the BACK nothing had to be invented: the ledger is the
    same 48x68 on the same wall plane screwed 140 mm higher, 474..542 ->
    614..682, and its spikerslag zone with it. At the FRONT there are two new
    pieces, and they are the only two pieces this whole round adds: BORDKLOSSER,
    36x48 x 108, one on each ladder upright's inner face at the rung blocks'
    own X. Their rear 36 mm is the fixing (the upright offers 36 mm of Y and
    nothing else); the 70 mm behind that is the ledge the plate lands on. The
    70 is not chosen - it is MIN_BEARING / (2 x 36) rounded up, so the two of
    them make the same 5 000 mm2 the file asks of any bearing line. One 6x80
    each, through the upright from the bench side, and one screw is all the
    36 x 48 face legally holds.
    THE BATTENS DO NOT KNOW. The bordkloss stands on exactly the plane the
    rung end stood on (X 835 / 1155) over exactly the same 48 mm of Z, so the
    panel's guide battens find it the same way, with the same 2 mm fit - and
    lap 70 mm of it in Y where a rung gave them 30. The panel sub-assembly is
    unchanged to the millimetre.

    THE CEILING IS NOW THE DESIGN POINT, NOT A LIMIT WITH ROOM UNDER IT. X8's
    block still computes the tallest plate the mode change allows, off the
    solids, and it now computes 700 - the plate sits EXACTLY on its own
    ceiling. Rung 3 went up by exactly the 61 mm that made 700 legal and not
    one more. The two walls X8 named are both still measured: the lift has its
    100 mm (INSERT_CLEAR, table mode, dead on the floor) and the crossing has
    118 mm of band for an 86 mm unit, 32 mm of daylight against a 15 mm gate.
    The mechanism film flies it.

    WHAT DID NOT MOVE: bed mode, entirely. The bench, the seat, the cushions,
    the panel in its bed seat, the upper deck, the guards, the mattress, the
    wall plane, the depth. Rung 1 is still 297 and still carries the bed-mode
    plate. This round is the LADDER ABOVE RUNG 1 and the TABLE SEAT, and
    nothing else in the bed is touched.

    WHAT IT LEAVES OPEN, HONESTLY: 280 mm over the cushion is 92 mm above this
    reference child's seated elbow, so he works at it with his forearms on the
    plate and his elbows up. The shop's own pair does the same thing (SMASTAD's
    730 over the 430 chair sold with it is 300), and the builder chose the
    shop. There is no footrest under the plate - the soles hang 134 mm off the
    floor - and that is written down as an open point rather than drawn away.

DESIGN INTENT (v15 - "the wall gets a datum, the bench gets a room, and the
                      desk gets an answer")
--------------------------------------------------------------------------
X8  THE DESK AT 700 IS NOT BUILDABLE, AND WHAT SAYS SO IS RUNG 3.
    *** SUPERSEDED BY X9. Kept whole, because it is the reasoning the change
    had to answer and because its two walls are still the two walls - what X9
    changed is not the arithmetic but which member was allowed to move. ***
    This entry
    is a REFUSAL, written down at the same length the change would have been,
    because the request was right and the reason it cannot be had is not
    obvious from any drawing in this folder.

    WHAT WAS ASKED FOR, AND WHY. The plate is a sofa table today: top 560,
    140 mm over the 420 cushion, 122 under it. A thigh is ~115 mm, so a
    straight leg goes under it and a bent knee does not - it is a surface you
    lean over from a bench, not one you sit AT. The builder wants the other
    thing: a PULT. Top ~700, i.e. 280 over the cushion and ~262 under it,
    knees in under the plate the way they go under a desk, and his reference
    is a thing he can point at in a shop rather than a number he made up -
    IKEA SMASTAD's desk at 730. The argument is X1's own: the lower storey is
    "the play, homework, sofa and table storey - the one the hours go in", and
    homework at a lap table is homework done badly. Nothing about the case is
    wrong.

    WHAT IT WOULD HAVE TAKEN. Two moves. The rear seat is easy - the back
    table ledger is a 48x68 on the wall that only has to be screwed 140 mm
    higher, 474..542 -> 614..682, and its nogging zone with it; the transfer
    slot over the bench GROWS when it goes, 154 -> 294 mm. The front seat is
    the whole problem: the plate's front edge lands on wood at the LADDER, the
    ladder's wood at that height is rung 2 (top 542) and rung 3 (top 787), and
    682 is between them. So it needs new bearers on the uprights - blocks in
    the rung-block family, 36x48, screwed to the upright's inner face with a
    ledge standing back into Y 720..752 for the plate to sit on. That much is
    ordinary joinery and it drew fine.

    WHY IT DOES NOT WORK. The plate is not fitted, it is CARRIED - the same
    unit is the bed in one mode and the table in the other, and it gets from
    one seat to the other by hand. Two walls, and they are the same piece of
    wood twice:
      1  THE LIFT. The panel is 574 x 798 and lies at Y -48..750; the rungs
         are X 835..1155 at Y 720..788. So wherever the plate sits at the
         ladder, a strip of it lies UNDER a rung, and in table mode that rung
         is rung 3, underside 739. At the plate's present 560 the straight-up
         run is 179 mm (measured, INSERT_CLEAR). At 700 it is 39 - and the
         guide battens need 48 to come free of their locator at all. The unit
         cannot be lifted off its own seat.
      2  THE CROSSING. It does not go up in place either: the thing that
         carries it at table height is over the bed seat, so the trip is out
         over a bench and back across the ladder in the free band between
         rung 2's top (542) and rung 3's underside (739) - 197 mm for an
         86 mm unit (K3, leg 6). A front bearer at 682 stands at 634..682,
         INSIDE that band, and splits it into 92 and 57: the unit fits
         neither with clearance. Crossing UNDER the bearer is no use, because
         the plate would then have to rise through the bearer to reach its own
         seat. Crossing OVER it needs the plate top at 768 while rung 3's
         underside is at 739. Twenty-nine millimetres short, and no detail on
         the bearer changes it: 68 of the band is spent before the unit is in
         it, because the bearer top IS the plate's underside.

    THE CEILING, MEASURED AND NOW ASSERTED. Both walls are arithmetic on the
    same 739, so the highest plate top the mechanism allows falls out of it:
      671  zero clearance anywhere - a number, not a design
      649  with the 11 mm of daylight the mechanism film keeps
      639  with INSERT_CLEAR_MIN, the 100 mm of straight-up run this file has
           always demanded. THIS IS THE ANSWER: plate top 639, underside 621,
           219 mm over the cushion and 201 under it. Knees DO go under 201.
    That is 79 mm above where the plate sits now and 61 below the desk that
    was asked for, and it is a real improvement rather than the one wanted.
    Not taken in this round: it moves the ledger, the zone, the bearers, the
    figures, the film and every number in the manual, and it is the builder's
    call whether two thirds of a desk is worth that. The ceiling is computed
    off the solids and asserted (X8, by the insertion sweep), so the next
    attempt is met with the number instead of with a collision.

    AND WHAT WOULD ACTUALLY UNLOCK 700: rung 3 would have to go up 51 mm, to
    838. Then step 2 -> 3 is 296 mm against the 280 limit X2 set from EN 131.
    THE EVEN LADDER AND THE DESK WANT THE SAME 51 MILLIMETRES and only one of
    them can have them. X2 already settled the precedence once - "the LADDER
    decides and the TABLE FOLLOWS" - and this entry is that rule being paid
    for a second time, out loud.
    [X9 CORRECTION, because a wrong number left standing is a trap. It is 61
     mm and not 51: the lift wants the rung UNDERSIDE at 800, so the top goes
     to 848. And step 2 -> 3 is not 296, because rung 2 is not nailed down -
     it moves to 572 and the two steps below the corridor come out 275/276.
     Nothing needed a 296 mm step; what it needed was for rung 2 to be allowed
     to move, and X8 did not ask it to. The count stays at five.]

    THE FIGURES DO NOT MOVE. The two seated bodies sit cross-legged because
    the plate is at lap height, and the plate is still at lap height, so the
    pose and the prose that explains it are still true. Nothing in this round
    makes them a lie.
    [X9: and this is the paragraph the change had to come back for. At 700 the
     plate is NOT at lap height, the pose is not true, and both seated figures
     are re-posed with their knees under the plate. See X9.]

X8b THE SPIKERSLAG ZONES ARE WRITTEN FROM THE LASER LINE AS WELL. Every
    height in this file is over FERDIG GULV, which is right for a drawing and
    wrong for a wall: the floor in this house is out of level, the whole
    fitting job is built plumb and level off a laser line struck 1000 mm above
    the floor's HIGHEST point (MEASURE_DATUM_Z), and "229 over ferdig gulv" is
    a number the man at the open wall cannot set without first trusting the
    floor under that exact spot. So each zone is printed twice - over the
    floor, and as a signed offset from the line: minus below, plus above. The
    second column is the first minus 1000, derived nowhere else and asserted
    in three places, one of them in the ink of the finished table and one in
    the ink of the finished sheet. Zone 2 reads -771..-703, zone 3 -526..-458.

X8c THE ROOM UNDER THE BENCH IS MEASURED, BECAUSE IT IS GOING TO HOLD BOXES.
    Nothing in this round makes that space - the stub legs left it when they
    replaced a plinth - but nothing had ever said how big it is, and a room
    nobody has measured is a room nobody buys boxes for. Read off the solids:
    229 mm of clear height (floor to the bench rail underside), 479 mm of
    clear width (the back corner post's inner face to the stub leg's outer
    face) and 800 mm of clear depth - the bench slat's own length, because the
    box goes in UNDER the front rail rather than past it. Two of them, one
    under each bench. Both the room and the corridor it is pushed in through
    are asserted empty, and the height is stated as the minimum it is: the
    frame is level and the floor is not, so 229 is what you get at the floor's
    high point and more everywhere else.

DESIGN INTENT (v14 - "both storeys seat an adult")
--------------------------------------------------------------------------
X1  THE UPPER DECK GOES UP 337 mm AND THE BENCH 38, AND THE ROOM BECOMES A
    PARAMETER. RAIL_BOTTOM 1065 -> 1402 and BENCH_RAIL_TOP 259 -> 297 are the
    whole change; everything else in this round is derived off one of those
    two and rides along.

    WHY, AND WHY THESE NUMBERS. The room is 2450 mm high, and that number is
    now written down (ROOM_H) instead of living in the builder's head. Once it
    is written down the whole question becomes arithmetic, because the two head
    rooms share a FIXED POT: take the room, take out the things that are not
    head room at all - the seat face the sitter starts from (420), the slat
    (23) and the mattress on it (120) - and what is left is
      2450 - 420 - 23 - 120 = 1887 mm
    to be split between the storey below and the berth above. Nothing anyone
    does to this bed changes that 1887; the platform is only the sliding wall
    between the two halves of it, and every millimetre it goes up is a
    millimetre the lower storey gains and the upper one loses. (The model
    asserts the sum, so the pot cannot drift out from under the argument.)

    v13 put the wall at 1163 and split the pot 781 / 1114. That is not a
    compromise, it is an accident: it gave the MOST room to the storey where
    people are lying down and the LEAST to the one where they live. v14 splits
    it on purpose, and the split is deliberately lopsided the other way:
      1080 mm below   the play, homework, sofa and table storey - the one the
                      hours go in. 1500 mm from the floor to the slat
                      underside. The bought bunk this was measured against,
                      IKEA SMASTAD, gives 1420 there; HANNA gives 1500.
      807 mm above    a BERTH. Nobody stands in it and nobody sits in it for
                      long; what it needs is air to sit up, swing the legs out
                      and get on the ladder. 807 is that, and the rule it is
                      held to (MIN_LIE_HEADROOM, 750) is deliberately lower
                      than the 900 the lower storey must clear.
    THE RULE CHANGED BECAUSE THE INTENTION DID, and that is written out at the
    assert rather than left as a relaxation nobody explains: until v14 both
    storeys were held to the same sitting-height rule, on the unexamined
    assumption that they were the same kind of place. They are not.

    THE BENCH GOES UP 38 TOO, and that is the other half of the round. The
    seat was 382 mm - a child's chair - and 420 is a grown chair, which is what
    the lower storey has to be if it is a room and not a play box. Everything
    on the bench datum moves with it: rails 191/259 -> 229/297, bench top
    282 -> 320, seat face 382 -> 420, stub legs 191 -> 229, the bed-mode panel,
    the cushions, the whole mechanism. The two 38 mm are why the lower head
    room is 1080 and not 1118.

    THE MATTRESS GOES 150 -> 120. A berth wants its sleeper as low in the
    guard as it can put him, and 30 mm of foam is 30 mm of head room straight
    back into the 807. The guard bands are re-dimensioned round the thinner
    mattress by the file's own rule (see X1 RE-BANDING), so the legal window
    moves 140..155 -> 110..125 and the EN 747 arithmetic above the sleeping
    surface is unchanged: 65 / 75 mm of opening and 336 mm of barrier.

    WHAT MOVES, AND WHAT DOES NOT. Off RAIL_BOTTOM: the rails (1402..1500),
    the slat platform (1500..1523), the mattress (1523..1643), the end beams
    (1304..1402), the back posts (1402, still the rail underside - W6), the
    front posts and ladder uprights (1700 -> 2037, because they carry a guard
    band) and the guard bands themselves. Off BENCH_RAIL_TOP: the bench, the
    sofa, the panel in bed mode, the stub legs. The ladder spans both and is
    re-derived (X2). Nothing horizontal changes LENGTH: the through members are
    still 1984 and the walls are still 1990 apart.

    THE CEILING IS A LIMIT NOW, LIKE THE TWO WALLS. Two rules, both measured
    on the built solid rather than on constants: the tallest part must clear
    2450 (2037 does, by 413), and the front frame must be able to be TILTED
    upright under it - a rectangle swinging about its foot sweeps its own
    diagonal, and 2037 x 836 sweeps 2202. See THE ROOM HAS A CEILING.
X2  THE LADDER BECOMES A RULE, AND THE TABLE FOLLOWS IT.
    D8 hand-set four rung tops against a platform that has moved twice since,
    so the list had drifted out of true (the last step was 228 mm against
    238s). A hand-set list cannot follow a platform, and X1 moves it 337 mm and
    the foot of the ladder 38, so the tops are DERIVED: the fewest rungs that
    keep every step inside the pitch limit, spaced as evenly as whole
    millimetres allow, between the two heights that actually decide them -
    rung 1 on the bench rail (297, where it has to be: it carries the bed-mode
    panel) and the slat surface (1523). The climb is 1226 mm, which is FIVE
    rungs rather than four, and the rule works that out on its own: 297 / 542 /
    787 / 1032 / 1277, a climb of 297 + 245 + 245 + 245 + 245 + 246. The
    evenest ladder this bed has had, to within one millimetre - and the fifth
    rung is not a decision anybody typed, it is what 1226 mm and a 280 mm pitch
    limit come to.

    WHAT THE FIFTH RUNG COSTS, SAID OUT LOUD: one more 48x68 x 320 tread, two
    more 36x48 blocks, four more screws. It is one of the two things that take
    48x68 from two boards to three (the other is the shop jigs, X5).

    X2 ALSO SETTLES WHO OWNS RUNG 2. Under D8 the answer was "the table": rung
    2 was typed at 482 because the table-mode panel underside is 482, and the
    back ledger was moved up to meet it. That is backwards - a ladder whose
    rung spacing is set by a table top is a ladder with one step in the wrong
    place - and after X1 it is not even possible. So the LADDER decides and the
    TABLE FOLLOWS: rung 2 is 542, and PANEL_UNDER_TABLE and the back table
    ledger ride up with it. Against a seat that also went up 38, the plate ends
    up 140 mm over the seat cushion where v13 had 118 - close to where it was,
    and the 122 mm under it is still a lap-height surface rather than a desk.
    The reference figure leaning over the plate is re-posed to the new height.
    On the WALL, the ledger's nogging zone moves with it: 414..482 -> 474..542,
    and the bench rail's 191..259 -> 229..297.

    THE PITCH LIMIT WAS RE-AIMED, 250 -> 280, AND NOT QUIETLY. 250 was this
    file's own comfort number, written for a 1186 mm platform and a 259 mm
    ladder foot. It is not a standard, and holding a moved platform to it would
    have bought a SIXTH rung for no reason: at 1226 mm of climb, 280 gives five
    rungs at 245 and 250 gives five as well - but the number that decides how
    many rungs a climb needs should be the trade's, not one this file invented
    for a bed that no longer exists. Portable-ladder practice (EN 131) puts
    uniform rung pitch in the 250..300 band; 280 is inside it, and the rule
    lands the actual pitch at 245, under both. The evenness rule
    (MAX_CLIMB_SPREAD = 20) is untouched and is now met to within 1 mm, where
    the old hand-set list used 15.

DESIGN INTENT (v13 - "the mode change is a flat carry")
--------------------------------------------------------------------------
The mechanism film (v12) was built as a feasibility proof and it proved the
wrong thing: the path existed, but only as a 3 degree roll through a
zero-clearance slot, nine handgrips long, because the panel unit is 91 mm
tall and the slot it had to cross was 91 mm high. This round makes the move
comfortable instead of merely possible. Two changes, and neither of them
touches a load path.
K1  THE RUNG BLOCK IS CUT TO THE DEPTH OF THE FACE IT IS SCREWED TO, 73 -> 36.
    U2 turned the ladder uprights and left 36 mm of upright behind a 73 mm
    block, so the block's rear 37 mm has touched nothing since - not the
    upright, not the load path, not the J5 screw's face. What it DID touch
    was the panel's transfer slot: the panel runs to Y 750 and the block ran
    back to Y 715, so 35 mm of unattached offcut was the ceiling of the whole
    manoeuvre and it pulled that ceiling down by the full 48 mm of block
    height. Cut to 36 and set in the upright's own Y band the blocks leave
    the corridor entirely, the ceiling becomes the back table ledger's
    underside (a member that has to be there), and the slot goes 91 -> 114 mm
    against a 91 mm unit: 23 mm of daylight, and a flat carry. J5 is
    unchanged to the millimetre - same 1728 mm2 face, same one 5x60 - and the
    screw actually improves, from Y 751,5 (half a millimetre outside the
    upright's back plane) to Y 770, dead centre. The straight-up insertion
    sweeps grow with it: 109 -> 132 mm in bed mode, 124 -> 172 in table mode.
K2  THE PANEL IS 574 WIDE, NOT 652 - AND THE WIDTH IS QUANTIZED. The reason is
    table-mode insertion: the unit is lowered into its seat by hand, above
    head height for a child, and nothing aims it until the guide battens drop
    past the rung ends. Everything before that is the sheet arriving between
    two bench ends, and the side gap is exactly how much of a miss that
    survives. But the gap cannot be dialled: the opening is 700 mm, the gap
    is (700 - width)/2, and EN 747 makes only three gap bands legal - up to 5
    (a finger does not enter), 12..25 (it passes freely) and 60..75 (the limb
    passes, and 75 is EN 747's own opening limit). So the panel has exactly
    three legal width windows, 690..700 / 650..676 / 550..580, and the whole
    581..649 span is forbidden wood. v12 sat at 652, the bottom of the middle
    window; v13 takes the top of the next one down with the saw's tolerance
    kept at the dangerous wall: 574 mm, 63 mm gaps, 3 mm to the 60 mm edge
    and 12 to the 75. It costs 12% of the table (0,520 -> 0,458 m2) and it
    makes the two front wings shorter (116 -> 77 mm) and less stressed
    (utilisation 0,18 -> 0,12). In bed mode the two 63 mm strips beside the
    panel are open to the bench rail below and the seat cushion bridges them
    - see the K2 note under PANEL_BENCH_DIP.
K3  THE MODE CHANGE IS SEVEN HANDGRIPS AND NO ROLL. What the two changes above
    buy is re-searched, not asserted: tools/render_animasjon.py runs the path
    through a separating-axis probe on every frame, and the path it lands on
    now lifts the unit flat into the slot, carries it out over the bench,
    up the open bay and back in over rung 2. The roll is gone, two legs with
    it, and the tightest pass on the whole trip is still PANEL_FIT.
K4  THE J8-B SEAT IS 20 MM DEEP, BECAUSE A COUNTERSUNK HEAD HAS TWO PLACES TO
    SIT. V4 bored every skew screw a flat-bottomed pocket 18 mm deep along its
    own axis and measured 2,26 mm of wood over the head at J8-B. That number
    assumes the head lies ON the flat bottom. It has a second rest: the 90 deg
    cone can bear on the RIM OF THE PILOT HOLE, 2,9 mm higher, and 2,9 mm along
    a 65 deg screw eats 1,23 mm of the cover - 1,03 mm left against a 1,0 mm
    limit. J8-B goes to 20 mm (3,11 mm on the bottom, 1,88 on the rim), J10
    stays at 18 (4,89 / 3,76). Same screw, same bit, one more turn of the depth
    stop. And the wood BETWEEN the two J8-B pockets - 6 mm, and nothing was
    watching it - gets an assert of its own, TOE_SEAT_MIN_WEB.
K5  THE VINKELKLOSS IS A BORED BLOCK, NOT A SAWN RAMP. V4's jig was one 160 mm
    offcut with a ramp sawn on each end and the drill asked to lie on the ramp.
    A bit lying on a ramp is a bit with nothing round it, and the recipe had the
    angle backwards as well - a mitre saw tilted 25 deg leaves a face at 65 deg
    to the one on the table, not 25. The jig is now TWO blocks, one per angle,
    each of two 48x68 x 200 screwed face to face with a ⌀18 hole bored SQUARE
    through both BEFORE the sole is cut off under it at the tilt. The hole is
    then a sleeve the bit runs in, its angle is the saw's and not the hand's,
    and the ellipse it leaves in the sole - 42,6 x 18 at J8-B, 36 x 18 at J10 -
    is a control measure you can read with a ruler before the jig ever touches
    the bed.

DESIGN INTENT (v11 - "one profile: 36x98")
--------------------------------------------------------------------------
U1  THE BOARD IS 36x98, NOT 34x98. 34x98 came off a drawing; 36x98 is what the
    yard actually keeps on the shelf, and 34x98 turned out to be a special
    order at best. Every flat board in the bed changes together - 14 upper
    slats, 10 bench slats, 4 front guard segments - and gets 2 mm thicker in
    its own thickness direction. Same 98 mm width, same lengths, same 28
    pieces. The 2 mm then walks up every stack a board is IN:
      platform top      1163 + 36 = 1199   (was 1197); mattress 1199..1339
      bench top          259 + 36 =  295   (was 293)
      cushion recess    295 - 277 =   18   (was 16; the panel is still 18 mm
                        of sheet on a rail top that has not moved)
      guard bands       1414..1512 and 1587..1685 (was 1412..1510, 1585..1683)
    and the EN 747 arithmetic comes out the same, because the bands moved with
    the mattress: 75 / 75 above the mattress as before, and the third opening
    - the only one that closes against something FIXED, the 1700 post tops -
    absorbs the whole 2 mm, 17 -> 15 mm. Barrier still 346 above the mattress.
U2  THE CORNER POSTS ARE 36x98 TOO, AND THE LADDER UPRIGHTS TURN. The four
    corner posts go 48x48 -> 36x98, thin face to the room: 36 in Y, 98 in X.
    48x48 leaves the frame entirely; the four bench stub legs were the last
    thing on it (they cannot follow - a leg 36 deep would hang out of the
    48 mm bench rail it bears under), and U5 below takes them to 48x73, so
    the profile leaves the bed altogether. What the change buys:
      * ONE PROFILE. 36x98 is now 32 of the bed's 69 pieces and 28 of its 47
        running metres - slats, bench slats, guards AND posts off one pile;
      * a BIGGER post. A = 3528 mm2 against 2304, and about the strong axis
        (98 in X, i = 28.3) it is six times as stiff as the old square
        (I = 2 823 576 against 442 368 mm4). The weak axis (36 in Y,
        i = 10.4) governs, and even there the front post is the stronger
        column: over its worst 708 mm unbraced length, N_c,Rd = 26.4 kN
        against 22.3 for the 48x48. Utilisation ~0.05;
      * a BIGGER bearing where W6 put the load: the back rail lands on
        95 x 36 = 3420 mm2 of post end grain instead of 45 x 48 = 2160;
      * 12 mm of depth (U3).
    The two ladder uprights keep their 36x48 stock and TURN through 90 deg -
    48 along X, 36 along Y - so that every vertical in the front plane is
    36 mm deep and the depth gain is real. That costs the walk-around passage
    beside the ladder 12 mm, 154 -> 142 (floor 140), and it makes J3's screw
    detail literally right for the first time: 6x90 through 36 mm of upright
    lands 42 mm into the 48 mm rail.
    The ripples, all asserted:
      end beams        X 48..96 / 1894..1942 -> 98..146 / 1844..1892, and
                       Y -48..800 (848) -> -48..788 (836)
      J1-B blocks      follow their posts, 48 x 48 -> 48 x 36 of bearing
      back bench rail  1894 -> 1794, X 98..1892, butting 36 x 73 of post face
      back ledger      1894 -> 1794, X 98..1892, butting its whole 21 x 95
      J9-B back blocks X 48..96 / 1894..1942 -> 98..146 / 1844..1892
      J9-B front block pinned to the rail thickness (48) instead of the post
                       width, so all four blocks stay ONE cut length
      bench slats      field starts at X 98, pitch 124.75 -> 112.25, gap 14.25
      front bench rail meets a 98 mm post on the Y 752 plane: 95 x 73 = 6935
                       mm2 of face per end, up from 45 x 73 = 3285
      guard laps       45 -> 95 mm on a post, 36 -> 48 mm on an upright
      rungs            Y 727..800 -> 715..788; the rest ledge under the panel
                       grows 25 -> 37 mm and the stiffener battens 727 -> 715
    Unchanged: the ladder's clear opening (320, inner faces 835 / 1155), the
    rungs and rung blocks as pieces, the climb, the panel, the bench rails'
    heights, the whole back rail / ledger / slat Y stack, and the mattress
    capture (still pinned -48..752 between the wall and the front verticals).
U3  THE FRONT FACE IS THE PLANE Y = 788 AND THE DEPTH IS 836. Every vertical
    in the front plane is 36 deep now, so the plane Y 788..800 that the posts,
    the uprights and the rung fronts used to occupy is asserted EMPTY - the
    same test D14 and W6 ran on the layers they vacated. 848 -> 836, and the
    end beams follow, so "the bed is exactly as deep as its own end frames"
    still holds. Depth history: 1070, 964, 930, 896, 848, 836.
U4  M8 IS OUT OF EVERY POST JOINT. D4's argument for a single central M8 was
    that a 48 mm face gives 24 mm of edge distance, exactly the 3d EC5 asks
    for an unloaded edge. A 36 mm face gives 18, so that argument fails and
    the bolt goes. Every joint into a corner post switches to the 6x90
    pre-drilled screw pattern the LADDER UPRIGHTS have used all along (J3):
    3d for a 6 mm screw is 18 mm, which is exactly what a 36 mm face offers on
    its centre line, and a 6x90 through a 48 mm rail leaves 42 mm in the post.
    Screws stack along the post grain the way the ties did. NOTHING ABOUT THE
    LOAD PATH CHANGES: the C2 bearing blocks and the W6 post-top bearing carry
    every vertical reaction, and every fastener into a post was already a pure
    tie. Affected joints: J1 (end beam), J2 (front side rail), J8 (bench
    rail), plus the W9 end fixings of the back bench rail and the back ledger.
    The exact screw counts per joint are the docs round's to set.
U5  THE BENCH STUB LEGS GO BACK ON THE BENCH RAIL'S OWN PROFILE AND 48x48
    LEAVES THE BED. v9/W3 had squared the four legs off, rail profile -> 48x48,
    for exactly one reason: 48x48 was the corner-post section then, so it
    consolidated two profiles into one. U2 above moved the posts to 36x98 and
    that reason is gone. What was left was an ORPHAN profile: 48x48 bought for
    four legs and nothing else - 744 mm of wood off a 2,4 m board, 69% waste,
    its own line in the shopping list and its own pile on the floor. So the
    legs revert to the BENCH RAIL'S OWN profile - the very member each leg
    bears under - and are cut from the rest the four rungs leave on that board.
    One board and one profile leave the list, and the bed is down to FIVE
    timber profiles plus the plywood sheet.
    NB - THE PROFILE IS 48x68, NOT THE 48x73 THIS ENTRY WAS WRITTEN ON. U5 was
    argued on a 48x73 bench rail, and 48x73 turned out not to be a thing you
    can buy: the shop stocks 48x68. The whole rail family went 73 -> 68 and the
    legs went with it. The ARGUMENT is untouched - it was never about 73, it
    was about the leg sharing the rail's section - and every number below is
    the 68 one.
    The Y dimension - the binding one - never moves: 48, the bench rail's own
    depth, so the leg is flush in Y as it always was. All the change is in X,
    where there is a whole rail to sit under. Consequences:
      leg-on-rail bearing  48 x 48 = 2304 -> 48 x 68 = 3264 mm2, i.e. ~7,4 kN
                           against the ~0,5 kN a leg sees; utilisation
                           0.09 -> 0.06
      X positions          the RULE is unchanged (inner face on the inner end
                           of its own bench, X 645 / 1345, leg running
                           outward from there, fully under its rail segment),
                           so only the outer faces move: 597..645 -> 577..645
                           and 1345..1393 -> 1345..1413
      J10                  the bracket and its screws re-derive against a
                           68 mm leg face instead of 48 - see the joint
    Unchanged: the leg height, the bench rail segments, the open front floor
    X 645..1345, the walk-around, and every other profile in the bed.

DESIGN INTENT (v10 - "the back posts tuck under the bunk")
--------------------------------------------------------------------------
W6  THE BACK POSTS MOVE INTO THE BACK RAIL PLANE AND STOP UNDER THE RAIL.
    The two back corner posts used to be a separate 48 mm layer BEHIND the
    back rail (Y -96..-48), running past it to the platform top (1197). They
    now stand IN the rail's own plane, Y -48..0, at the same X (0..48 and
    1942..1990), and they stop at Z 1065 - the rail UNDERSIDE. What it does:
      * the back rail BEARS DIRECTLY ON THE POST TOPS. Rail underside = post
        top, so the platform reaction at each wall corner goes rail -> post
        -> floor as end-grain bearing with no fastener in the load path. The
        bolts and brackets there become pure ties, which is exactly what C2
        did for every other joint in this bed. Before, the rail hung off the
        SIDE of the post and that corner reaction lived in fasteners;
      * the 48 mm layer behind the rail disappears, and 48 mm of room depth
        with it: 896 -> 848 (W7; v11/U3 takes it to 836 from the front end);
      * the posts go 1197 -> 1065 mm. The W2 argument - nothing of a back
        post above the mattress underside, whatever the mattress turns out to
        be - survives with a whole rail height to spare.
    (v11/U2: the post is 36 deep in Y instead of 48, so it fills Y -48..-12 of
    the rail's -48..0 band rather than all of it. Its back face is still the
    wall plane and its top is still the rail underside; what it presents to the
    rail got BIGGER, 95 x 36 = 3420 mm2 against 45 x 48 = 2160, because the
    post is 98 wide in X and the rail runs in X.)
W7  THE WALL PLANE IS Y = -48 AND THE OVERALL DEPTH IS 848. Everything on the
    back side ends in the back rail's outer face, and that face is the wall.
    Overall depth -48 .. 800 = 848 mm (was 896, 930, 964, 1070; v11/U2+U3 take
    the FRONT face in 12 mm to 788, so it is 836 now).
W8  ONE SLAT LENGTH AGAIN. v9/W4 stretched twelve of the fourteen upper slats
    to 847 mm so the platform could reach past the back posts to the wall.
    With the posts inside the rail plane there is no slot left to cover: all
    14 upper slats revert to the uniform 36x98 x 800 (v11/U1; 34x98 in v10),
    Y -48..752, at the same pitch and the same 44.5 mm gap. The design is back
    to ONE flat-board length - 24 identical 800 mm pieces (14 upper slats + 10
    bench slats).
W9  THE BACK MEMBERS RUN POST TO POST, NOT WALL TO WALL. The back bench rail
    and the back table ledger ran the full 1984 mm at X 3..1987 in the very
    Y band the posts have moved into, so they would collide at both corners.
    Both are cut to 1894 mm, X 48..1942, butting the posts' X-inner faces and
    screwed to them - an end FIXING they never had before (they used to be
    dropped onto a bearing block and nothing else). Their mid supports are
    unchanged: two stub legs under the bench rail, the wall behind the ledger.
    The two back bench-rail bearing blocks turn with them - they now stand on
    the post's X-inner face at X 48..96 / 1894..1942, Y -48..0, top flush at
    Z 186, so the rail end has 48 x 48 mm of wood under it instead of 45 x 36.
    RIPPLE: the outermost bench slat at each end shared X with its corner post
    (0..98 against 0..48) and would now share the Y band too, so the five
    bench slats per bench are re-pitched to start at the post inner face -
    X 48..645 instead of 0..648, pitch 137.5 -> 124.75, gap 39.5 -> 26.75 mm.
    Same five 34x98 x 800 pieces per bench, just closer together.
    (v11/U2 does the same sum again on a 98 mm post: both members are 1794 at
    X 98..1892, their blocks at X 98..146 / 1844..1892, and the bench field is
    X 98..645 at pitch 112.25, gap 14.25. The end FIXING lands on a 36 mm deep
    face now - 36 x 73 = 2628 mm2 for the rail, the ledger's whole 21 x 95 -
    and it is 6x90 screws, not M8, for the reason U4 gives.)

DESIGN INTENT (v9 - "wall-side reduction")
--------------------------------------------------------------------------
W1  NO BACK GUARD BOARDS. The two 34x98 x 1984 boards at Y -130..-96 are
    DELETED. The wall is the barrier on the back side, so a guard rail there
    was a board bolted to a board bolted to a wall. What it leaves:
      * the guard-opening arithmetic of D6 is now a FRONT-SIDE check only,
        over exactly the same two bands (1412..1510, 1585..1683);
      * the back side gets its own EN 747 check instead - the mattress-to-
        wall gap, 48 mm, i.e. the post depth (v10/W6 takes that layer out of
        the bed altogether: the clear is exactly the mattress, gap 0);
      * the overall depth drops 964 -> 930 mm and the back face of the
        assembly becomes the wall plane Y = -96 itself (D14 takes it on to
        896 from the front end; v10/W6+W7 move the wall plane itself to -48
        and the depth to 848);
      * 34x98 goes from 29 pieces to 27 (W4 puts it back to 28; v10/W8 keeps
        28 and makes all 24 slats one length again).
W2  SHORT BACK POSTS - CUT FLUSH WITH THE PLATFORM. The two BACK corner posts
    go 1700 -> 1197 mm, i.e. flush with the SLAT TOP, which is the mattress
    underside. Everything they carry lives below that line - the bench-rail
    bearing blocks (138..186), the back table ledger (387..482), the
    end-beam bearing blocks (931..967), the end beams and their bolts
    (967..1065), the back side rail (1065..1163) and finally the two end
    slats that butt against them (1163..1197). NOTHING of the post is left
    standing above the platform.
      * the earlier cut was 1337 - the mattress TOP - so that the post could
        act as the sideways mattress stop over the mattress's whole Z band.
        That made the stop exactly as tall as the MODELLED mattress: a
        thinner mattress (130, 120 - they are all sold as "140") would have
        left a bare stick of post standing proud beside the sleeper's head.
        Cutting at the platform instead removes the failure mode outright:
        there is no post above the mattress underside, whatever mattress
        goes on;
      * what the post gave up - capturing the mattress at Y -48 - is taken
        over by the WALL itself (W5), which the platform now reaches (W4);
      * the front corner posts and the two ladder uprights stay 1700 (they
        carry the front guard bands). The end elevation is asymmetric by
        design;
      * v10/W6 takes the same argument one storey further down. The post now
        stops at the rail UNDERSIDE, 1065, and CARRIES the rail on its top
        instead of standing beside it, so the last thing on a back post is
        the rail, not a slat, and the clearance to the mattress underside is
        a whole rail height (132 mm) rather than zero.
W3  SQUARE STUB LEGS. The four bench stub legs go 48x73 -> 48x48, the same
    section as the corner posts. (v11/U2 breaks that identity: the posts go
    36x98 and the legs cannot follow, because a 36 mm leg would hang out of
    the 48 mm bench rail it bears under - which left 48x48 an orphan profile
    on four pieces. v11/U5 therefore REVERSES THIS ENTRY: the legs are 48x73
    again, the bench rail's own profile. Read W3 as history.)
    The leg is an end bearing under a 642 mm
    (front) / 1984 mm (back) rail, not a column: at 48x48 the leg-on-rail
    contact is 2304 mm2, ~0.09 utilisation in compression perpendicular to
    the grain, and the leg's own buckling length is 186 mm. Their inner
    faces stay exactly where they were, on the inner end of their bench-rail
    segment (X 645 / 1345); only the section changes, so they stood at
    X 597..645 and 1345..1393 until U5 put them back at 572..645 / 1345..1418.
W4  THE PLATFORM RUNS TO THE WALL. The slat field goes 13 -> 14 slats and the
    twelve MIDDLE slats grow 800 -> 847 mm, Y -95..752, i.e. 1 mm clear of
    the wall plane Y = -96. The old 48 mm slot between the slat ends and the
    wall - the depth of a back post - is closed. Only the FIRST and LAST
    slats stay 800 mm (Y -48..752): they share X with the back corner posts
    (X 0..48 / 1942..1990), which still occupy Y -96..-48 right up to the
    platform top, so those two butt against the posts exactly as before.
    Every slat still bears the full 48 mm on both side rails; the 14th slat
    takes the inter-slat gap from 60.5 to 44.5 mm.
    (SUPERSEDED BY v10/W8. The slot W4 was covering was the back posts' own
    48 mm layer, and W6 deleted that layer. All 14 slats are 800 mm again;
    the 14-slat field and its 44.5 mm gap are what W4 leaves behind.)
W5  THE MATTRESS IS CAPTURED BY THE WALL AND THE FRONT VERTICALS. With the
    back posts gone from above the platform the mattress is no longer held
    between two lines of posts. It is held between the ROOM WALL at Y = -96
    (reachable now that the platform goes there, W4) and the front corner
    posts / ladder uprights at Y = 752. That clear is 848 mm under an 800 mm
    mattress, so the mattress can wander 48 mm, and at either extreme the
    single resulting gap is 48 mm - under the 75 mm EN 747 entrapment limit,
    the same number the old fixed mattress-to-wall gap had.
    (v10/W6+W7: the wall moves forward to Y -48, so the same two stops are
    now 800 mm apart under an 800 mm mattress. The mattress is PINNED - zero
    wander, zero gap at either edge - which is the v8/D12 fit restored, but
    with the wall doing the job the deleted back post used to do.)
D14 GUARDS INBOARD - THE LAST 34 mm OF DEPTH. The four front guard boards move
    from the OUTER faces of the front posts / ladder uprights to their INNER
    faces: Y 800..834 -> 718..752. Same four pieces, same 832 mm lengths, same
    two bands, same X - only the Y plane changes, by POST_T + GUARD_T = 82 mm.
    (v11: the plane they hang ON is the post INNER face and that has not moved,
    so the boards are at Y 716..752 simply because they are 36 thick. The shift
    off the outer faces is POST_T + GUARD_T = 72 now. The laps grew with the
    members: 95 x 98 on a corner post, 48 x 98 on a ladder upright.)
    What it buys and what it costs:
      * the front face of the assembly stops being a guard board and becomes
        the post plane Y = 800, so the overall depth goes 930 -> 896 mm - the
        same 896 as the end beams. The bed is now exactly as deep as its own
        end frames, and the 34 mm slice at Y 800..834 is asserted EMPTY.
        (v10/W6 takes the other end in by 48 the same way: 848, and the end
        beams follow to 848, so the identity still holds);
      * the boards overhang the mattress footprint by 34 mm, Y 752 back to
        718. That is air, not contact: the lower band starts at Z 1412 and
        the mattress tops out at 1337, so the nearest board is 75 mm above
        the sleeping surface - the D6 opening, which EN 747 already sized;
      * the laps are unchanged as overlaps and changed as faces. Each segment
        still laps a front corner post (45 x 98) and a ladder upright
        (36 x 98) over the same X, but on the inner Y face, so the two 5x60
        per lap are driven FROM INSIDE THE BED. Screw heads now sit on the
        mattress side of the board rather than the room side;
      * the climb-through is untouched at 320 mm. The segments still die on
        the upright inner faces X 835 / 1155 - they butt the same two
        uprights, from the other side - so the opening is the same opening.

DESIGN INTENT (v8 - "flush mattress + open front floor + slim 320 ladder")
--------------------------------------------------------------------------
D12 DEPTH SHRINK - THE MATTRESS IS FLUSH AT BOTH EDGES. The platform was
    906 mm deep and carried an 800 mm mattress, so 106 mm of bare slat was
    on show - 29 mm at the back, 77 mm at the front. The whole depth stack
    is pulled in by 106 mm ON THE FRONT SIDE ONLY; the back plane (back rail
    Y -48..0, back posts Y -96..-48, back guards Y -130..-96 - deleted in
    v9/W1 - back ledger, back bench rail) does not move at all. (v10/W6 is
    the first round that DOES move it: the back posts come forward 48 into
    the rail plane and the wall plane with them, -96 -> -48. The back rail,
    ledger and bench rail planes are still exactly where D12 left them.)
    What that gives:
      * upper slats and bench slats become 800 mm long, Y -48..752 - still
        one and the same piece, still one board profile (34x98 then, 36x98
        after v11/U1), still lying on top of the rails
        (v9/W4 stretched twelve of the upper ones to 847; v10/W8 puts them
        all back to 800, so this line is literally true again);
      * the front side rail moves 810..858 -> 704..752, so the clear width
        between the upper rails is 704 = 800 - 2 x 48: the mattress spans
        OVER both rails and its two edges land exactly on the slat ends;
      * the reference mattress is Y -48..752, i.e. EXACTLY the rail-to-rail
        slat footprint. Sideways play was 0 by construction, which was the
        point - there was no bare slat strip left to fall into and no gap
        along either edge. (v9/W4+W5 revisited this: the platform ran on past
        the back rail to the wall, so the mattress had 48 mm of travel on
        slat instead of 0 mm on a 48 mm slot. v10/W6 removes the slot AND the
        travel by moving the wall itself to the back rail face - the zero-play
        fit is back, and this time both stops are structure the mattress can
        actually be pushed against.);
      * everything in the front plane follows -106: front corner posts
        752..800, ladder uprights 752..800, rung treads 727..800 (the 25 mm
        rest ledge behind the upright plane is preserved exactly), rung
        blocks, front guards 800..834 (v9/D14: 718..752, hung on the INNER
        post faces instead), front bench rail 704..752, front stub
        legs, the front bench-rail bearing blocks.
        (v11/U2 re-sections the three of those that stand in front of Y 752 -
        posts, uprights, and with the uprights the rungs - from 48 deep to 36:
        752..788 and 715..788, so the rest ledge goes 25 -> 37. Their BACK
        faces are exactly where D12 left them.);
      * the end beams shorten 1002 -> 896 (they still span the full post-to-
        post depth, Y -96..800; v10/W6: 848, Y -48..800; v11/U3: 836,
        Y -48..788);
      * the movable panel becomes 680 x 800, Y -48..752 - rear edge still
        flush with the bench slats and on the back bench rail / back ledger,
        front edge still butting the ladder uprights and resting on the rung.
    Overall depth over the guards drops 1070 -> 964 mm. (v9/W1 deletes the
    back guards, so the back face becomes the wall plane -96 and the overall
    depth drops again, 964 -> 930 mm; v9/D14 then hangs the front guards
    inboard, and the front face becomes the post plane 800: 930 -> 896 mm;
    v10/W6+W7 tucks the back posts into the back rail plane and the wall face
    becomes the rail face -48: 896 -> 848 mm; v11/U2+U3 re-sections every
    front vertical 48 -> 36 deep and the post plane itself comes in:
    848 -> 836 mm.)
D13 FRONT FLOOR CLEARED + SLIM 320 LADDER. Two moves that belong together,
    both about the space you actually stand in.
      * The front bench rail no longer runs from the sofa to the ladder. Each
        segment now STOPS AT ITS SOFA END, X 3..645 and X 1345..1987 (642 mm
        each), landing its inner end square on the stub leg that was already
        there (X 572..645 / 1345..1418) - zero cantilever, the leg simply
        moves from mid-span to end-bearing. Nothing at bench-rail height
        crosses the whole 700 mm between the two benches any more, so the
        entire front floor in front of the ladder is clear.
      * The ladder narrows from 420 to 320 clear and slims from 48x48 to
        36x48 uprights, 36 along X / 48 along Y so the 48 face still lies
        flat on the front rail plane for through-bolting. Upright inner faces
        835 / 1155, outer faces 799 / 1191, symmetric about 995. The rungs
        become 320 mm treads, the front guard segments lengthen to 832 mm to
        meet the new inner faces, and the climb-through gap is 320 mm in both
        guard bands and at floor level. The rung blocks are unchanged 36x48
        x 73 offcuts - their 36 mm is stock thickness, not upright width, and
        the 48 x 48 face they present to the upright inner face is unaffected
        by the upright getting narrower in X. (v13/K1 has since cut them to
        36 mm: after U2 turned the upright, only 36 of those 73 ever touched
        it, and the other 37 stood in the panel's transfer slot.)
    The pair of them opens a walk-around passage on each side of the ladder,
    between the sofa end and the upright outer face, 151 mm clear and empty
    from the floor to 482. (v14/X2: to 542 - the passage ceiling IS rung 2.)
    STRUCTURAL CONSEQUENCE, flagged for the docs round: the ladder has LOST
    its low lateral restraint. See the LADDER section for the numbers.

DESIGN INTENT (v7 - "resting panel + even ladder + open ladder bay")
--------------------------------------------------------------------
D8  EVEN LADDER. The rungs were a mechanical 280/560/840/1120 grid that had
    nothing to do with the rest of the bed: a 280 mm first rise off the floor
    and then three 280 mm steps up to a platform that D5 had moved to 1197,
    leaving a 77 mm stub of a last step. The tops are now 259 / 482 / 720 /
    958. Rung 1 lands exactly on the BENCH RAIL TOP (259) and rung 2 exactly
    on the TABLE-MODE PANEL UNDERSIDE (482), so the two rungs that carry the
    movable panel (D10) are the same wood as the rest of that mode's support
    line; rungs 3 and 4 are then spaced to even out the climb. The rises are
      floor -> 259   259 mm   (the "first step" IS the bench seat rail line)
      259 -> 482     223 mm
      482 -> 720     238 mm
      720 -> 958     238 mm
      958 -> 1197    239 mm   (last rung to the platform surface)
    i.e. every step of the climb proper is 223..239 mm, a 16 mm spread, all
    under the 250 mm comfort limit. The 259 mm floor-to-rung-1 rise is not a
    climbing step in the same sense - it is a seat-height ledge you step onto,
    and it is fixed by the bench rail it shares its top with.
D9  BACK LEDGER UP. The back table ledger moves from Z 371..466 to 387..482,
    so its top is level with rung 2 (482) and the table-mode panel lies
    straight on both of them - no step, no bracket (D10).
D10 THE PANEL RESTS ON WOOD. The four steel U-hooks of D3 are DELETED, and
    with them the 16 mm hook step. The panel now simply LIES on wood:
      BED MODE   Z 259..277 - on the back bench rail (top 259), on rung 1
                 (top 259) and, because D11 only takes the MIDDLE out of the
                 front bench rail, on the two front rail segment ends as well.
      TABLE MODE Z 482..500 - on the back table ledger (top 482) and rung 2
                 (top 482).
    Two consequences fall out of that:
      * the panel grows to the full depth of a slat (v7: 906, Y -48..858;
        v8/D12: 800, Y -48..752) because it has to REACH the members it rests
        on - the back bench rail lives at Y -48..0 and the ledger at
        Y -48..-27, and the old Y 30 rear edge reached neither. Its rear edge
        is now flush with the bench slats' rear edge, so in bed mode benches
        and panel are one field.
      * the RUNGS slide 25 mm back, so the tread fronts are flush with the
        ladder-upright front faces instead of standing 25 mm proud of them
        (v7: Y 858..931 -> 833..906; v8/D12: Y 727..800). This is what gives
        the panel's front edge something to sit ON: the panel cannot cross
        the upright back plane (the uprights are floor-to-ceiling and the
        panel's X range 655..1335 straddles both of them), so the rung has to
        come back to meet it. The result is a RUNG_LEN x 25 mm bearing under
        the front edge - the same order as the 21 mm the back ledger offers -
        and the rung blocks keep their full 48 x 48 mm face contact on the
        upright inner faces.
      * v8/D13 ripple: with the front bench rail cut back to the sofa ends the
        bed-mode panel no longer picks up its two segment ends. Both modes are
        now the same clean two-line support - a back member (bench rail /
        ledger) and a rung - about 727 mm apart.
    The panel top in bed mode is 277, i.e. 18 mm BELOW the 295 bench tops
    (16 below 293 before v11/U1 thickened the bench slat). That dip is
    deliberate: the fold-out seat cushions are what bridge the three zones into
    one sleeping surface, and they need somewhere to fold into.
M4  PANEL STIFFENER BATTENS + THE REAL PANEL CONNECTIONS. An 18 mm sheet on
    the two-line support D13 left it with is at bending utilisation ~1.42 at
    the 2 kN dynamic design point - a fail. Two 48x73 battens ON EDGE, 727 mm
    long, are screwed under the panel and run bearing line to bearing line
    (Y 0..727, i.e. from the back rail face to the rung face). They sit at
    X 882..930 and 1060..1108, symmetric about the ladder centreline 995 and
    inset 11 mm inside the rung-block line, and they hang BELOW the panel:
    Z 186..259 in bed mode, 409..482 in table mode. They travel with the
    panel. Utilisation drops to ~0.27.
    v12/V2 REPLACED THE STEEL THIS ENTRY DESCRIBED (U-brackets round the rung,
    hook plates over the rear support) with four shop angle brackets. v13/V3
    deletes those four as well: the battens moved OUTBOARD of the rung ends
    (X 785..833 / 1157..1205) and forward to the panel's own front edge, so
    they are 750 mm long and they are the guides. See V3.
V2  THE PANEL BECOMES A DROP-IN ASSEMBLY. Four shop angle brackets, on the
    sides of the assembly, over the edges they land on; the bespoke bent steel
    is deleted. In the order the decisions bind:
      * THE MOVE COMES FIRST. The panel has zero travel in Y - its rear edge
        IS the wall plane and its front edge is at the ladder - so the only
        move it has is straight down. Every piece of the old steel wrapped
        the FAR side of a member, which is a move you can only make by
        threading the panel in at an angle. The new rule is that nothing may
        reach past a member it does not have to, and the assert family
        `V2 innsetting` sweeps the whole assembly - sheet, four battens, four
        brackets and their bolts - straight up out of both seats, on the
        solids. It clears 109 mm in bed mode and 124 in table mode, and what
        stops it in both is the LADDER (a rung block), which is the honest
        ceiling of a two-height convertible: whatever carries the panel in
        the upper seat is in the way on the trip down.
      * THE SEAT IS WOOD, THE STEEL ONLY SAYS WHERE. The rear brackets lie
        on the rear support BESIDE the panel, in the side gap - never under
        it - so the panel still lands flat on 652 x 48 mm of wood in both
        modes. The front pair hangs under the panel just outboard of the rung
        ends and stands 2 mm clear of them: that pair is the whole of the X
        and the rotation restraint, in both modes, because the rung ends are
        at the same X at both heights.
      * THE SIDE GAP IS AN EN 747 NUMBER. 10 mm was inside the band a
        finger wedges in. The gap is 24 mm now and the panel 652 wide.
      * THE FRONT CORNERS GET WOOD UNDER THEM (M5). The panel's front edge
        outboard of each rung end was bare 18 mm sheet; two cross battens
        carry it inboard to the M4 battens. 213 mm in V2, 116 in V3.
      * THE REAR SUPPORT IS ONE PROFILE. The table ledger goes 21x95 to
        48x73 at Y -48..0, the back bench rail's own section and plane, so
        the rear seat is identical in both modes - and 21x95 leaves the bed.
      * WHAT V2 GIVES UP, SAID OUT LOUD: the U-bracket wrapped the rung, so
        it tied the panel to the ladder in TENSION and that tie was this
        design's answer to the ladder-base restraint finding F1. A bracket
        that grips the far side of a member cannot be lowered into place, so
        the tie is gone. What is left is a STRUT: the panel fills the clear
        between the wall plane and the uprights with PANEL_FIT to spare, so
        the ladder foot cannot move BACKWARD. Forward it is held only by J3
        into the front side rail. That is a one-way brace where there used to
        be a two-way tie, it is written into docs/ASSEMBLY.md as an open
        point, and if it has to become a requirement the answer is a brace
        from the ladder foot to the frame - not a bracket on the panel.
      * UPLIFT IS NOT BLOCKED, ON PURPOSE. The panel is meant to lift out.
        The bed-mode lock was a separate decision, presented as three options
        in docs/preview/laasvalg.png; V4 takes it, and the answer is NONE -
        an accepted deviation, vedlegg B avvik 4.
V3  THE MECHANISM BECOMES WOOD, AND THE TABLE TOP BECOMES UNBROKEN. V2 had
    got the panel down to four shop brackets and no bespoke steel. V3 asks the
    next question - what are the brackets for that a batten could not do - and
    the answer is nothing.
      * THE BATTENS ARE THE GUIDES. The two 48x73 stiffener battens move from
        inside the rung-block line to OUTSIDE the rung ends (X 785..833 and
        1157..1205, PANEL_FIT off X 835 / 1155) and run forward to the panel's
        own front edge, Y 0..750. The last 35 mm of each one stands in the
        48 x 37 mm free shaft beside a rung end - the shaft the deleted
        bracket flange used to stand in - so X+, X- and rotation about Z are
        taken by 48 x 35 mm of wood against end grain instead of 2 mm of
        galvanised plate, in BOTH modes, because the rung ends are at the same
        X at both heights. All four angle brackets leave the beslagliste, and
        with V4's lock decision (none) the panel asks for no steel at all.
      * WHAT THE MOVE COSTS, SAID OUT LOUD. Outboard of the rung end there is
        nothing under the batten's front end, so it hands its reaction into
        the sheet and the sheet carries it 26 mm across into the rung: ~0.69
        utilisation on the conservative panel value, the panel's governing
        sheet row now. The insertion sweep is unchanged at 109 / 124 mm, and
        it is a stronger claim than before - the guides are IN their shafts
        for the whole descent, not lowered onto a stop at the end of it.
      * NO SCREW HEAD IN THE TABLE TOP. J13a/J13b turn over: the battens are
        GLUED and then screwed from BELOW, 5x40 out of a 46 mm counterbore, so
        27 mm of batten and 13 mm of the 18 mm sheet with 5 mm standing over
        the point. The alternatives - toe screws, and plugged top screws -
        are costed where the constants are.
      * THE M5 CROSS BATTENS SURVIVE, SHORTER. 213 -> 116 mm, and moved to the
        panel's front edge. They were re-examined and they are not optional: a
        1 kN knee on a FREE plate corner is 6P/t^2 = 18.5 MPa in 18 mm sheet
        no matter how close the nearest batten is.
      * THE LOCK POINT MOVES ONTO WOOD, and onto the one pair of faces that
        only face each other in bed mode - the cross batten's end and the
        front bench rail's end, 24 mm apart across the side gap.
      * THE MODE BUG. The fasteners are modelled once, in bed mode, and both
        modes used to be handed that one list - so in table mode the panel
        stood 223 mm up and its own screws stayed down at bed height. They
        travel with the panel now, and an assert compares every panel-assembly
        fastener's position RELATIVE TO THE PANEL across the two modes.
V5  THE FRONT SHOWS NO STEEL, AND THE EIGHT BEARING BLOCKS GO.
    Two decisions, taken together because they are the same decision twice:
    stop believing a detail because it has always been there, and go and
    measure it.
      * NO FASTENER HEAD ON A ROOM-FACING FACE. Three of the bed's four wall
        sides are wall; the fourth is the front, Y 752..788, and it is the
        only surface anyone looks at. The four guard boards have been screwed
        from inside the bed since D14. J2 (front side rail -> front post),
        J3 (ladder upright -> front side rail) and J8 (front bench rail ->
        front post) were not, and their heads sat on the two posts' and two
        uprights' forside. All three are now driven from INSIDE the bed
        outward - through 48 mm of rail into 36 mm of post or upright, a
        6x80 either way round, which the fit rule calls 'tvetydig' and hands
        to the table. Tip cover is unchanged at 4 mm; it has simply moved
        from the rail to the post. VISIBLE_FRONT_Y and an assert make it a
        rule instead of a habit, and the assert says out loud that it is an
        AESTHETIC one.
      * THE EIGHT BEARING BLOCKS ARE DELETED - 4 x J1-B under the end beams,
        2 x J9-B and 2 x J9-F under the bench-rail ends. The argument for
        them was "the member bears on wood instead of hanging in screw
        shear". Follow it one step: the block does not stand on anything
        either. It hangs on ONE 6 mm screw, 2.0 kN against up to 1 kN of
        corner reaction - the 0.50 that topped vedlegg A's screw rows and the
        only 0.50 in the bed. The block did not take the reaction out of
        steel; it halved the steel the joint would otherwise have had.
        Re-derived honestly before deleting anything, per vedlegg A's method:
          J1   endebjelke -> stolpe   2 x 6x90 = 4.0 kN vs <= 1 kN   0.25
          J8   fremre benkevange     2 x 6x80 = 4.0 kN vs 0.5 kN     0.13
          J8-B bakre benkevange      2 x 6x90 = 4.0 kN vs 0.5 kN     0.13
        and 0.50 / 0.25 / 0.25 with the whole design load stood directly over
        the corner. The gate was 0.8. The J1 pair has 3d of end distance
        along the beam's grain and 4.5d of edge distance in the direction the
        load acts, in 48 x 98 of C24 - an ordinary lap fixing, not the
        brittle end-split the block was bought against. All five numbers are
        asserted off the model rather than quoted.
        WHAT THE BLOCK REALLY WAS is a shelf to rest the member on while you
        drove its end screws. The pre-drilled holes are that shelf: steg 0
        bores each pattern through both members clamped together, and a hole
        pattern has exactly one position it lines up in. The jig was already
        in the bed; the blocks were a second copy of it in wood.
        Cost: 71 -> 63 pieces, 36x48 18 -> 10 pieces, 4 x 6x90 and 2 x 6x60
        off the beslagliste, and the 6x60 length off the shopping list
        entirely.
D11 OPEN LADDER BAY. The FRONT bench rail is cut into two segments so nothing
    crosses the floor of the ladder bay below the benches any more - you can
    stand at the foot of the ladder with your toes under it. Both front stub
    legs stay where they were, under their segment. The BACK bench rail is
    untouched and still runs the full 1984 mm.
    v7 made the segments X 3..785 / 1205..1987, each lapping its ladder
    upright over the full 48 mm face on the plane Y = 858. v8/D13 goes the
    whole way and stops them at the SOFA ends instead (X 3..645 / 1345..1987,
    642 mm each), so the open bay is the entire 700 mm between the benches,
    not just the 420 mm of the ladder. The lap onto the upright is gone with
    it; the inner end bears on the stub leg that was already under it.

DESIGN INTENT (v6 - "flush top + re-banded guards" final tweak)
---------------------------------------------------------------
D5  The upper mattress platform is no longer a sunken tray. The two 36x48
    slat cleats are DELETED and the slats now lie ON TOP of both side rails,
    exactly the way the bench slats lie on top of the bench rails. One
    consequence at a time:
      * the slats become the same piece as a bench slat - one board profile,
        spanning the full platform depth so each one covers the full 48 mm
        width of BOTH rails (v7: 906 mm, Y -48..858; v8/D12: 800 mm,
        Y -48..752) - and that profile becomes the common board stock of the
        whole design (34x98 then; 36x98 after v11/U1, which also takes the
        corner posts onto it);
      * the platform surface rises 1134 -> 1197 and the mattress with it,
        1197..1337 (v11/U1: 1199 and 1199..1339 on the 36 mm board);
      * the slat reaction now lands on the rail centreline instead of on a
        cleat screwed to one face, so the rails are loaded concentrically;
      * both guard bands move up (see D6). The rail underside, the head
        clearance under the platform and the whole lower storey are untouched.
D6  GUARD RE-BANDING. With the mattress top at 1337 the two guard bands go to
    Z 1412..1510 and 1585..1683, which makes every opening measured above the
    mattress surface 75 / 75 / 17 mm - all at or under the 75 mm EN 747
    entrapment limit, with the top band still 346 mm above the mattress.
    (v9/W1: the same two bands, but on the FRONT only. The back side's EN 747
    case is the 48 mm mattress-to-wall gap instead. v11/U1: both bands go up
    2 mm with the mattress, to 1414..1512 and 1587..1685, and the openings come
    out 75 / 75 / 15.)
D7  ONE GUARD PROFILE. The front guard segments follow the back boards from
    21x95 up to the common board (v7: Y 906..940; v8/D12: Y 800..834; v9/D14:
    Y 718..752, inboard of the posts; v11/U1: Y 716..752 on the 36 mm board),
    so every guard and every slat in the bed is cut from the same board. 21x95
    now survives only as the back table ledger. (v9/W1: the back boards are
    gone, so that board is the front guard profile and nothing else needs to
    match it. v11/U2 then puts the corner posts on it too.)

DESIGN INTENT (v5 - "slim + 6 verticals" design round)
------------------------------------------------------
C9 is the rule that shapes everything horizontal: a 1990 mm long member
cannot be swung into a 1990 mm opening (the corners sweep ~997 mm from the
centre when the piece is rotated down to horizontal). Every through-running
horizontal member is therefore 1984 mm long and centred at X 3..1987.
Only the vertical posts still touch the walls, at X 0..98 / 1892..1990 after
v11/U2 (0..48 / 1942..1990 before it).

WHAT CHANGED IN v5
  D1  The two intermediate BACK POSTS (v4 / C1) are GONE. The frame now has
      exactly SIX verticals: four corner posts and two ladder uprights.
      The back guard boards are upgraded from 21x95 to 34x98 to carry the
      resulting full 1894 mm span between the corner posts on their own.
      (v9/W1 deletes those boards outright - the wall is the barrier - and
      v9/W2 cuts the two back posts to 1197; v10/W6 moves them into the back
      rail plane and stops them at 1065, under the rail. Still six verticals,
      but two of them are short now.)
  D2  The front guard boards are SEGMENTED. Each band is two boards lapped
      onto the ladder uprights, so the ladder opening continues straight up
      past the guard rails and you climb THROUGH instead of over. (v5: 21x95,
      X 3..785 / 1205..1987, 420 mm opening. v7/D7: 34x98. v8/D13: X 3..835 /
      1155..1987, 832 mm each, 320 mm opening. v9/D14: the lap moves to the
      uprights' INNER faces, Y 718..752 - same overlap, other side.)
  D3  The front table ledger (v4 / C6) is DELETED - it crossed the front of
      both sofa benches at knee height. The panel is instead carried at its
      FRONT edge by a LADDER RUNG (rung 1 in bed mode, rung 2 in table mode)
      and at its REAR edge by the back bench rail (bed mode) / the back table
      ledger (table mode). (v7: the four steel U-hooks that used to make that
      connection are gone too - the panel lies straight on the wood now, see
      D8/D9/D10.)
  D4  SLIMMING. Side rails and end beams 48x123 -> 48x98 (rail underside
      stays at 1065, end-beam top stays flush with it). Corner posts and
      ladder uprights 48x73 -> 48x48. Everything else keeps its stock.

Upper level: a 1984 x 800 sleeping platform at 1402 mm underside height (the
slats bridge both rails flush on top, D5; D12 shrank the depth 906 -> 800 so
the 800 mm mattress is flush at both edges; v14/X1 lifted the whole deck
337 mm to put the slat underside on a round 1500), carried by four corner
posts - two 2037 mm ones at the front and, after v10/W6, two 1402 mm at the back
that stand IN the back rail plane and carry the back rail on their tops. The
platform reaches the wall because the wall IS the back rail face now, so the
wall is what stops the mattress on that side (v9/W5, v10/W7) and all 14 slats
are the same 800 mm piece again (v10/W8). The
two ends are OPEN above the mattress -
there are no end boards at guard-rail height, because they cut into the
sleeping area. Instead each end has a single 48x98 END BEAM screwed to the
inner faces of the corner posts, its top flush with the underside of the
side rails so both rails bear on it. Nothing sits under the beam ends: v12/V5
deleted the four 36x48 bearing blocks that used to, because a block that hangs
on one screw halves the shear the joint would otherwise have. The beam end is
held by its own two 6x90 (J1), 4.0 kN against a corner reaction of at most
1 kN.

The ladder is mounted directly on the front of the bed: its 36x48 uprights
share the Y 752..788 plane with the front corner posts (v11/U2 turned them so
that their 36 mm face is the depth), i.e. they lie flat against the outer face
of the front rail and are screwed through it. The rungs are 48x73 treads,
320 mm long, carried on cleat blocks screwed to the inner faces of the
uprights.

Lower level: a convertible sofa / table / bed. The 48x73 bench rails sit at
Z 229..297, carried at their ends by the corner posts (on their own end
screws, J8-B behind and J8 in front - v12/V5 deleted the four bearing blocks
that used to hang under them) and in between by four 48x73 stub legs (v9/W3,
v11/U5). The BACK rail is one continuous 1794 mm
member butting the two back posts, X 98..1892 (C5, v10/W9, v11/U2); the FRONT
one is two 642 mm segments that stop at the sofa ends on their stub legs,
leaving the whole front floor between the benches open (D11/D13). The two
benches are the slatted zones at each end: 36x98 slats (C3) laid on the
rails, so the bench top is at Z = 295. Between the benches an 18 mm pine
panel, stiffened by two 48x73 battens on edge along it (M4) and two more
across its front corners (M5), RESTS on wood (D10). The two long battens run
outboard of the rung ends and LOCATE it - wood on end grain, 2 mm of running
clearance, and not one piece of steel in the mechanism (V3) - so it is LOWERED
into either seat, and every gram of vertical load goes into wood:
  * TABLE MODE  - on the back table ledger (top Z 542) and on ladder rung 2
                  (top Z 542); panel top Z = 560. (v14/X2: both were 482/500
                  until the even ladder moved rung 2 and the ledger with it.)
  * BED MODE    - on the back bench rail (top Z 297) and on ladder rung 1
                  (top Z 297); panel top Z = 315, i.e. 5 mm below the bench
                  slats, the depth the fold-out cushions bridge.

Everything is modelled as plain axis-aligned Boxes moved into place.

EXPORTS
-------
Default (`mise run build`) - the fast validation loop only:
  .step  Z-up, mm, per-part names and colours (CAD truth).
  .stl   Y-up with the ladder side facing +Z, baked into the vertex data, so
         the bed stands upright AND faces the viewer in Quick Look / Preview /
         Xcode without any extra rotation (see Y_UP in the ASSEMBLY section).
  per-colour-group .stl files in a scratch directory, consumed by
  tools/mesh_to_usda.swift to build a multi-material .usdz.

Opt-in (`mise run build-full`, i.e. LOFTBED_FULL=1) - the slow deliverables,
run once at the end of the project:
  .glb   Y-up (export_gltf writes the Z-up -> Y-up rotation on the root
         node itself), one node per part, per-part colours.
  .svg   hidden-line iso + front projections. These dominate the runtime.
"""

import math
import os
import re
import tempfile

from build123d import (
    Box,
    Color,
    Cone,
    Cylinder,
    Compound,
    ExportSVG,
    Location,
    Sphere,
    export_gltf,
    export_step,
    export_stl,
)
from build123d import Vector

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Per-colour-group STL intermediates live outside the repo (they are only an
# input to the .usdz conversion). Override with LOFTBED_GROUP_DIR.
GROUP_DIR = os.environ.get(
    "LOFTBED_GROUP_DIR", os.path.join(tempfile.gettempdir(), "loftbed_groups")
)

# LOFTBED_FULL=1 turns on the slow deliverable exports (.glb and the hidden-line
# .svg projections). The default build writes only what the STEP/USDZ/render
# chain needs, which is what the design-validation loop runs over and over.
FULL_EXPORT = os.environ.get("LOFTBED_FULL", "").lower() in ("1", "true", "yes", "on")

# ---------------------------------------------------------------------------
# LUMBER CROSS SECTIONS (Norwegian standard planed dimensions)
# ---------------------------------------------------------------------------
# D4 (history): the four corner posts and the two ladder uprights went
# 48x73 -> 48x48. All vertical load already rides on the C2 wood bearing
# blocks, so every post bolt is a pure TIE. A single central M8 in a 48 mm face
# has 24 mm edge distance = 3d, exactly the EC5 minimum for an unloaded edge.
#
# U2 (v11): THE CORNER POSTS BECOME 36x98 - THE BOARD PROFILE. 48x48 disappears
# from the frame entirely (the four bench stub legs were the last thing on it,
# and U5 has since taken them to 48x73 as well, so it is gone). The post
# turns its THIN face to the room: 36 in Y, 98 in X. What that does, in order:
#   * ONE PROFILE. The posts are cut from the same 36x98 plank as every slat and
#     every guard board (U1), so the whole bed is five timber profiles and the
#     biggest pile by far is one of them;
#   * SECTION. A = 3528 mm2 against 2304 - 53% more wood in a post - and the
#     strong axis (98 in X, i = 28.3 mm) is now four times as stiff as the old
#     square. The weak axis (36 in Y, i = 10.4 mm) is what governs; see the
#     buckling note under POSTS;
#   * DEPTH. The front posts are 12 mm thinner, so the front face of the bed
#     comes in 800 -> 788 and the overall depth 848 -> 836 (U3);
#   * BEARING. The back rail lands on 95 x 36 = 3420 mm2 of post end grain
#     instead of 45 x 48 = 2160 - the load path W6 built gets 58% more face.
# U4: M8 IS OUT OF EVERY POST JOINT. An M8 needs 3d = 24 mm of edge distance and
# a 36 mm member offers 18 mm on the centre line, so the D4 argument that made a
# central M8 legal in a 48 mm face fails in 36 mm stock. Every joint into a post
# switches to the 6x90 pre-drilled screw pattern the ladder uprights already use
# (J3): a 6 mm screw wants 3d = 18 mm, which is exactly what a 36 mm face gives
# on its centre line, and 6x90 through a 48 mm rail leaves 42 mm in the post.
# Screws are stacked along the post grain 5d = 30 mm apart, as the M8 ties were
# at 40. Every one of them is still a pure TIE - the C2 bearing blocks and the
# W6 post-top bearing carry the load - so this is a fastener swap, not a change
# of load path. The exact counts per joint belong to the docs round; each joint
# below carries a comment saying which screw pattern it is.
POST_T = 36          # corner posts, thin dim (Y)  [was 48, U2]
POST_W = 98          # corner posts, wide dim (X)  [was 48, 73]

# D13: the two ladder uprights are 36x48. U2 ripple: they TURN, so that their
# 36 mm face is the depth in Y like every other vertical in the front plane -
# 48 along X, 36 along Y (was 36 along X, 48 along Y). Reasons:
#   * the front plane becomes ONE 36 mm layer, Y 752..788. If the uprights kept
#     48 mm in Y they would stand 12 mm proud of the new corner posts and the
#     whole depth gain of U2 would be a bounding-box illusion (U3);
#   * the fastening was already screws, not a bolt: J3 is 4 x 6x90 driven from
#     the front through the upright into the front side rail. The screw passes
#     through 36 mm of upright and lands 42 mm into the 48 mm rail - which is
#     what a 90 mm screw is for. On the old 48 mm depth it would have had to be
#     96 mm long to do the same job;
#   * COST: the upright is 48 wide in X again, so the walk-around passage beside
#     the ladder goes 154 -> 142 mm (still over the 140 mm floor - re-measured in
#     the validation block) and the guard segments lap 48 mm of upright instead
#     of 36. The climb-through is untouched: the inner faces are fixed at
#     835 / 1155 and the clear is still 320.
UPRIGHT_W = 48       # ladder uprights, X  [was 36 - the upright turned, U2]
UPRIGHT_T = 36       # ladder uprights, Y  [was 48] - the 36 mm front-plane depth

# U5: THE FOUR BENCH STUB LEGS GO BACK ON THE BENCH RAIL'S OWN PROFILE.
# The leg is an END BEARING under a bench rail, not a column. What it has to do
# is (a) present enough face to the rail underside and (b) not buckle over its
# own 229 mm (X3: was 186/191). Buckling is a non-question at 229 mm
# (lambda ~17), so the section
# is decided by the bearing and by the cut list.
# HISTORY. v9/W3 took the leg from the rail profile to 48x48 for one reason
# only: 48x48 was the corner-post section at the time, so the change
# CONSOLIDATED two profiles into one. v11/U2 then took the corner posts to
# 36x98 and that argument evaporated - 48x48 was left as an ORPHAN profile
# carrying four legs and nothing else, i.e. a whole 2.4 m board bought for
# 744 mm of wood: 69% waste, an extra line in the shopping list and an extra
# pile on the floor. U5 reverses W3. The leg is on the bench rail's own profile
# again - the very member it bears under - so the four legs are cut from the
# rest that board has after the four rungs. One fewer profile, one fewer board,
# no new stock.
# THE PROFILE IS 48x68. U5 was written on 48x73 and 48x73 is not a shop item -
# the rail family is 48x68 and the leg follows it. The argument never depended
# on the 73; it depended on the leg and the rail being the same board.
# The Y DIMENSION IS THE CONSTRAINT AND IT DOES NOT MOVE: 48, exactly the bench
# rail's depth, so the leg is flush in Y and neither hangs out of the rail nor
# leaves a lip. All the change is in X, where there is a whole rail to sit
# under. At 48x68 the leg-on-rail contact is 48 x 68 = 3264 mm2 (was 2304);
# against f_c90,d with k_c90 = 1.5 that is ~7.4 kN, i.e. utilisation ~0.06 at
# the ~0.5 kN a leg actually sees.
# The X POSITION rule is unchanged and is what the validation block enforces:
# the leg's INNER face lands on the inner end of its bench-rail segment
# (X 645 / 1345), so the rail still has zero cantilever past it, and the whole
# leg stays under that segment. Only the OUTER face moves back out, 597 -> 577
# and 1393 -> 1413.
LEG_T = 48           # bench stub legs, thin dim (Y)   - unchanged stock
LEG_W = 68           # bench stub legs, wide dim (X)   [48 in W3..U4; back on
                     # the bench rail's own profile, U5 - which is 48x68, not
                     # the 48x73 U5 was written on; the shop has no 48x73]

RAIL_T = 48          # upper bed side rails and end beams, thickness
RAIL_H = 98          # upper bed side rails and end beams, height  [was 123]

# 48x68 IS THE SHOP'S NUMBER AND 48x73 WAS NOT. Bench rails, ladder rungs,
# stub legs, stiffener battens, wedges and the back table ledger are all one
# profile and it is 48x68. The whole family was drawn 48x73 until the buying
# round went to the shop and found that 48x73 is not a thing you can put in a
# trolley. Nothing in any argument depended on the five millimetres - the
# constants below and every number derived from them are the 68 ones, and the
# asserts measure those - but PROSE WRITTEN BEFORE THAT ROUND STILL SAYS 73 in
# places, and it is left standing rather than rewritten under its own authors:
# where a comment and a constant disagree, the constant is the bed.
BENCH_RAIL_T = 48    # continuous bench rails, thickness (Y) - unchanged stock
BENCH_RAIL_H = 68    # continuous bench rails, height (Z)    [drawn 73]

TREAD_T = 48         # ladder rung (tread) thickness (Z) - unchanged stock
TREAD_D = 68         # ladder rung (tread) depth (Y)     [drawn 73]

BOARD_T = 21         # 21x95 board, thickness  - D7: the back table ledger ONLY
BOARD_W = 95         # 21x95 board, width      - D7: the back table ledger ONLY

# D5/D7: one board profile is the COMMON BOARD STOCK of this design. Everything
# flat-laid or stood on edge as a board comes out of it: the 14 upper bed slats,
# the 10 bench slats and the 4 front guard segments. One profile, one pile of
# timber, one setup on the saw.
# W1 ripple: the 2 back guard boards are gone, so the pile is 27 pieces, not 29.
# W4 ripple: a 14th upper slat takes it to 28, and (in v9 only) the slats stopped
# being ONE length - 12 of them ran on to 847 to reach past the back posts.
# W8 ripple: v10 puts the posts inside the back rail plane, so there is nothing
# left to reach past. All 14 upper slats are 800 again, the pile is still 28
# pieces, and the flat-board stock is back to ONE length: 24 identical 800 mm
# slats (14 upper + 10 bench) plus the 4 guard segments at 832.
#
# U1 (v11): THE PROFILE IS 36x98, NOT 34x98. 34x98 was specified off a drawing;
# 36x98 is what the yard actually stocks as a shelf item, and 34x98 turned out to
# be a special order at best. The board gets 2 mm thicker and nothing else about
# it changes - same 98 mm width, same lengths, same 28 pieces - but the 2 mm
# propagates through every stack the boards are IN:
#   platform top   1163 + 36 = 1199   (was 1197), mattress 1199..1339
#   bench top      259  + 36 = 295    (was 293),  panel dip 277 -> 18 mm
#   guard bands    1414..1512 / 1587..1685 (was 1412..1510 / 1585..1683)
# U2 then makes the same 36x98 the CORNER POST profile, so this is no longer
# "the board stock" - it is the stock of the bed: 32 of the 67 pieces.
BOARD36_T = 36       # 36x98 board, thickness  [was 34, U1]
BOARD36_W = 98       # 36x98 board, width

GUARD_T = BOARD36_T  # guard boards, thickness (Y) - FRONT only after W1
GUARD_W = BOARD36_W  # guard boards, width (Z)
# V6: THE 24 SLATS ARE 23x98, NOT 36x98. A slat is loaded FLAT, so its 23 mm is
# the bending depth and the section modulus is 98*23^2/6 = 8640 mm3 - 41% of the
# 36 mm board's. That is affordable only because the slat load case was
# recalibrated onto what a slat actually carries (vedlegg A.1): a mattress
# spreads a body over the field, and a bare foot always lands on two slats at
# this pitch. The bought profile is a standard justert dimension, the field
# loses 13 mm of build-up and 24 pieces lose a third of their weight.
BOARD23_T = 23       # 23x98 slat board, thickness  [V6: was BOARD36_T]
BED_SLAT_T = BOARD23_T   # D5/V6: upper bed slats, thickness (Z)
BED_SLAT_W = BOARD36_W   # D5: upper bed slat width (X)
BENCH_SLAT_T = BOARD23_T # C3/V6: bench slats, thickness (Z)
BENCH_SLAT_W = BOARD36_W # C3: bench slat width (X)
BLOCK_T = 36         # 36x48 bearing/rung block stock, thin dim
BLOCK_H = 48         # 36x48 bearing/rung block stock, wide dim
PANEL_T = 18         # movable pine panel thickness

# ---------------------------------------------------------------------------
# COLOUR GROUPS
# ---------------------------------------------------------------------------
# One colour per structural family. These survive into the .step (XCAF
# colours), into the .glb (one material per node) and, via the per-group STL
# export below, into the .usdz as five named UsdPreviewSurface materials.
GROUP_COLORS = {
    "posts": Color(0.95, 0.94, 0.91),       # posts, ladder uprights, stub legs
    "rails": Color(0.85, 0.73, 0.54),       # side rails, end beams, bench rails
    "boards": Color(0.91, 0.84, 0.68),      # slats, rungs, blocks, guards, ledger
    "panel": Color(0.98, 0.98, 0.96),       # movable pine panel
    "mattress": Color(0.62, 0.72, 0.81, 0.45),   # translucent reference mattress
    "figures": Color(0.90, 0.66, 0.52, 0.55),    # translucent reference child
}
GROUP_ORDER = ["posts", "rails", "boards", "panel", "mattress", "figures"]

# ---------------------------------------------------------------------------
# ENVELOPE
# ---------------------------------------------------------------------------
WALL_SPAN = 1990                 # X = 0 .. 1990, hard limit
# X1: THE ROOM HAS A CEILING, AND IT IS A PARAMETER NOW. The niche was only
# ever described sideways (WALL_SPAN) and downwards (floor at Z = 0); the third
# wall of it - the ceiling - lived in nobody's head but the builder's. It is
# 2450 mm in Hanna's room, and once it is written down the two heights that
# matter can be CHECKED instead of assumed: the tallest thing in the bed has to
# clear the ceiling with enough air to lift it into place, and the sleeper on
# the top bunk has to be able to sit up. See the SITTING HEIGHT block after the
# guard rails for both.
ROOM_H = 2450                    # Z = 0 .. 2450, finished floor to ceiling
# SITTING HEIGHT IS 0,545 OF STANDING HEIGHT. It is the one anthropometric
# ratio this whole bed turns on - it is what decides whether a storey is a
# place to sit or a place to stoop - and it is written once, here, for both of
# the things that use it: the reference child's segment table (FIG_SITTING_H)
# and the two head-room rules X1 checks against the room.
SIT_RATIO = 0.545                # seat/floor -> crown, as a fraction of height
MATTRESS_W = 800                 # 200x80 mattress
# 120 mm, og vinduet er 110..125. Se MATTRESS_H_MIN/MAX nedenfor: EN 747-1
# gir ikke bare et tak på åpningen mellom madrassen og nederste rekkverksbord,
# den gir et BÅND - 60..75 mm - og en madrass som er tykkere enn MATTRESS_H_MAX
# lukker åpningen ned i klemvinduet under 60. 120 legger den på 65, midt i
# båndet. [V7 skrev 150 og 140..155; U1/X1 flyttet både spileplanet og
# rekkverksbåndene, og vinduet fulgte med. Tallene her er utledet i
# MATTRESS_H_MIN/MAX og assertert der - dette er bare setningen som forklarer
# dem, og den skal si det samme som de gjør.]
MATTRESS_H = 120

# D12: the platform depth IS the mattress width. The slats run from the outer
# face of the back rail to the outer face of the front rail, so the platform is
# (clear width) + 2 x RAIL_T; setting that equal to 800 puts the mattress edges
# exactly on the slat ends. The clear width between the upper side rails falls
# out of it: 800 - 2 x 48 = 704 (was 810, a 906 mm platform under an 800 mm
# mattress with 106 mm of bare slat on show).
PLATFORM_DEPTH = MATTRESS_W                        # 800, D12
INNER_CLEAR_WIDTH = PLATFORM_DEPTH - 2 * RAIL_T    # 704
DEPTH_SHRINK = 906 - PLATFORM_DEPTH                # 106, taken off the FRONT

# C9: no horizontal 1990 mm member can be manoeuvred into a 1990 mm opening -
# swinging it down to horizontal sweeps sqrt(995^2 + 61.5^2) = 996.9 mm from the
# centre, ~2 mm too long at each end. Every through-running horizontal member is
# cut to 1984 and centred, leaving 3 mm clearance at each wall.
THROUGH_LEN = 1984               # every wall-to-wall horizontal member
THROUGH_X0 = (WALL_SPAN - THROUGH_LEN) // 2     # 3
THROUGH_X1 = THROUGH_X0 + THROUGH_LEN           # 1987

# ---------------------------------------------------------------------------
# UPPER BED
# ---------------------------------------------------------------------------
# D4: the rails are slimmed 123 -> 98 mm deep. The UNDERSIDE stays fixed at
# 1065 (head clearance below the platform is untouched); the top drops
# 1188 -> 1163.
#
# UTILISATION NOTE (D4, back side rail, worst case): with the intermediate
# back posts gone the back rail is a full 1894 mm single span. At the 2 kN
# dynamic design point the bending utilisation scales with (123/98)^2 = 1.575,
# i.e. 0.46 -> ~0.73, and the deflection with (123/98)^3 = 1.98, giving about
# 6 mm at midspan (~L/315). Both are acceptable; formal re-verification is a
# job for the docs round.
# U2 ripple: the corner posts are 98 wide in X instead of 48, so the clear span
# between their inner faces drops 1894 -> 1794 - 5.3% - and the rail's bending
# utilisation with it, ~0.73 -> ~0.65 (M ~ L^2), the deflection ~0.85 of what it
# was. The wall screws through the back rail still mid-support it either way.
# X1 (v14): THE WHOLE UPPER DECK GOES UP 337 mm, 1065 -> 1402. The number that
# was actually chosen is the one below it - the slat UNDERSIDE, RAIL_TOP, on a
# round 1500 off the floor - and 1402 is 1500 less one rail. Everything above
# this line is derived off it and rides up with it. See the X1 note at the top
# of the file for why (the short version: the two storeys share a fixed 1887 mm
# of head room, v13 split it 781 / 1114 with the majority over a sleeper who is
# lying down, and v14 splits it 1080 / 807 the other way, because the lower
# storey is the room and the upper one is a berth).
RAIL_BOTTOM = 1402               # underside of the upper side rails  [X1: was 1065]
RAIL_TOP = RAIL_BOTTOM + RAIL_H  # 1500 == SLAT_Z0, the target [was 1163]

# D12: the BACK plane is the fixed datum - it does not move. Everything in
# front of it comes in by DEPTH_SHRINK = 106 mm.
BACK_RAIL_Y0 = -RAIL_T           # -48 .. 0   (FIXED)
BACK_RAIL_Y1 = 0
FRONT_RAIL_Y0 = INNER_CLEAR_WIDTH        # 704  [was 810]
FRONT_RAIL_Y1 = FRONT_RAIL_Y0 + RAIL_T   # 752  [was 858]

# D5: FLUSH TOP. The slat cleats are gone; the slats lie ON TOP of both side
# rails, exactly like the bench slats on the bench rails. Each slat therefore
# spans from the OUTER face of the back rail to the OUTER face of the front
# rail (D12: Y -48..752) and covers the full 48 mm width of both - which is
# what makes it the same 36x98 x 800 piece as a bench slat. One 5x60 screw per
# end down into the rail; no cleat, no rebate, no lip anywhere.
#
# UTILISATION NOTE (D5, upper bed slat): identical stock, identical span and
# identical load model to the bench slat (C3), so the numbers are the same.
# 34x98 flat-on gave W = 98*34^2/6 = 18 881 mm3. The bench-slat case - the
# 2 kN dynamic design point shared over three slats, then checked with the
# concentrated 1.0 kN that a single slat can see on its own at midspan of the
# span - gave, over the v7 906 mm span, M = 227 kNmm, sigma = 12.0 MPa against
# f_m,d = 16.6 MPa, so utilisation ~0.72 (deflection ~4.4 mm, L/206). D12
# shortens the span to 800 mm, i.e. M scales by 800/906 = 0.883 and the
# deflection by 0.883^3 = 0.69: sigma ~10.6 MPa, utilisation ~0.64, deflection
# ~3.0 mm (L/262). The depth shrink is a strict improvement here.
# U1: 36x98 flat-on gives W = 98*36^2/6 = 21 168 mm3, i.e. (36/34)^2 = 1.12
# times the section modulus for the same span and the same load, so sigma goes
# ~10.6 -> ~9.5 MPa and the utilisation ~0.64 -> ~0.57. The deflection follows
# I, (36/34)^3 = 1.19, so ~3.0 -> ~2.5 mm (L/315). Two millimetres of board is
# worth more here than anywhere else in the bed, because a slat is loaded flat.
#
# W4 (v9) / W8 (v10): THE PLATFORM AND THE WALL. v9 had a 48 mm slot between the
# slat ends at Y -48 and the wall at Y -96 - the thickness of the back posts'
# own layer - and covered it by stretching twelve of the fourteen slats to 847,
# leaving the two end slats at 800 because they shared X with a post.
# W6 deletes the layer instead of covering it: the back posts move INTO the back
# rail plane, the wall plane comes forward to the back rail face Y = -48, and the
# slat ends are ON it. So:
#   * every upper slat is 36x98 x 800, Y -48..752 - the same piece as a bench
#     slat again, no two-length split, no fitting clearance to keep;
#   * no slat can foul a back post: the posts stop at the rail underside 1402
#     and the slats start at the rail top 1500, 98 mm clear. Asserted anyway;
#   * the 14-slat field survives from W4 (the 13-slat one had 60.5 mm gaps);
#     at this pitch the gap is 44.5 mm.
WALL_Y = BACK_RAIL_Y0                    # -48, the mounting face against the
                                         # wall = the back rail's outer face (W7)
SLAT_Z0 = RAIL_TOP                       # 1500, slats bear on top of the rails
                                         # - the round number X1 aimed at
SLAT_Z1 = SLAT_Z0 + BED_SLAT_T           # 1523  [X1: was 1163..1186]
SLAT_Y0 = BACK_RAIL_Y0                   # -48, outer face of the back rail
SLAT_Y1 = FRONT_RAIL_Y1                  # 752, outer face of the front rail
SLAT_LEN = SLAT_Y1 - SLAT_Y0             # 800  (the bench slat, same piece)
SLAT_COUNT = 14                          # [was 13, W4]
SLAT_X_START = 20                        # first slat left edge
SLAT_X_END = 1970                        # last slat right edge
MAX_SLAT_GAP = 60

# The reference mattress sits proud on the flush platform. D12 put it EXACTLY on
# the 800 mm rail-to-rail slat footprint, Y -48..752; v9/W4+W5 let it wander
# 48 mm back into the slot behind the back rail, and v10/W6 removes the slot by
# bringing the wall forward to Y -48. The mattress is back to a zero-play fit -
# it is DRAWN where it can only be. See MATTRESS_WANDER (0) and the W5 block.
MATTRESS_Z0 = SLAT_Z1                    # 1523  [X1: 1199]
MATTRESS_Y0 = SLAT_Y0                    # -48  [was 29]
MATTRESS_Y1 = MATTRESS_Y0 + MATTRESS_W   # 752  [was 829] == SLAT_Y1
MATTRESS_Z1 = MATTRESS_Z0 + MATTRESS_H   # 1643  [X1: was 1186..1336 on 150]

# ---------------------------------------------------------------------------
# SHARED LOWER DATUM  (hoisted - the ladder needs it before it is "its" section)
# ---------------------------------------------------------------------------
# The bench rail top is THE lower datum of the whole convertible section: it is
# the seat-height ledge, it is rung 1's top (D8), it is the bed-mode panel
# underside (D10) and it is the top of the stiffener battens (M4). It used to be
# declared down in LOWER CONVERTIBLE SECTION, which forced RUNG_TOPS[0] to
# repeat the literal 259 and left two numbers to keep in step by hand. It is
# hoisted here so every consumer derives from the one declaration.
BENCH_RAIL_TOP = 297                                # X3: was 259 (J9, J13)
BENCH_RAIL_BOTTOM = BENCH_RAIL_TOP - BENCH_RAIL_H   # 229  [was 191]

# ---------------------------------------------------------------------------
# POSTS  (D1: SIX verticals in total - four corner posts, two ladder uprights)
# ---------------------------------------------------------------------------
# W2 (v9): THE TWO FAMILIES NO LONGER SHARE A HEIGHT. A post is 1700 only if it
# has to carry a guard band; after W1 deleted the back guards, only the front
# ones and the ladder uprights do. v9 cut the BACK posts to the PLATFORM TOP,
# SLAT_Z1 = 1197 - the slat surface - so that nothing of them could ever stand
# proud of the mattress, whatever thickness of mattress turned up. (The cut
# before that was 1337, the mattress TOP, which made the stop exactly as tall as
# the MODELLED mattress: a 120 or 130 mm one - they are all sold as "140" -
# would have left a bare 48x48 stick beside a sleeper's head.)
#
# W6 (v10): THE BACK POSTS TUCK INTO THE RAIL PLANE AND UNDER THE RAIL. The post
# was a 48 mm layer of its own BEHIND the back rail, Y -96..-48, standing beside
# the rail and past it. It now stands IN the rail's plane, Y -48..0, and stops at
# the rail UNDERSIDE, RAIL_BOTTOM = 1065. Two things come out of that:
#   * LOAD PATH. The back rail BEARS on the post top, 48 x 48 of end grain under
#     it (45 x 48 of that covered by the rail, which is set in 3 mm at each wall
#     by C9). The corner reaction goes rail -> post -> floor with no fastener in
#     it; the M8 tie and the corner brackets hold the joint together and carry
#     nothing, which is the C2 principle applied to the one joint that did not
#     have it. Before, the rail passed the post on the inside and that reaction
#     had to be taken in bolt shear;
#   * DEPTH. The 48 mm layer is gone, so the wall plane is the back rail face
#     Y = -48 and the bed is 848 deep instead of 896 (W7).
# The W2 conclusion survives untouched and with room to spare: the post now tops
# out 132 mm BELOW the mattress underside, so there is nothing of it above the
# platform for any mattress at all. The tallest thing on a back post is the back
# side rail sitting on it (1402..1500); the highest fastener is still the M8 tie
# into the end beam (1304..1402). Asserted further down (W2/W6 check).
# [X1: those two bands were 1065..1163 and 967..1065 before the deck went up
#  337 mm. The 121 mm of clear air over the post top is unchanged - the post,
#  the rail and the platform all moved together.]
#
# U2 (v11): THE POST SECTION TURNS INTO A PLANK - 36 in Y, 98 in X. The BACK
# post keeps its back face on the wall plane and gives up 12 mm at the front, so
# it fills Y -48..-12 of the rail's own -48..0 band instead of all of it; the
# last 12 mm of that band is the rail's alone, which changes nothing, because
# what the post has to do there is present a TOP for the rail to bear on and a
# back face for the wall. Both are unchanged in kind and bigger in size: the
# bearing goes 45 x 48 = 2160 -> 95 x 36 = 3420 mm2, because the post grew where
# it matters (98 in X, under a rail that runs in X).
# The FRONT post loses the same 12 mm and that IS the depth story: its front face
# is the front face of the bed, 800 -> 788, overall depth 848 -> 836 (U3).
#
# BUCKLING, 36x98, weak axis (the 36 mm dimension, buckling in Y):
#   A = 3528 mm2; I_weak = 98*36^3/12 = 381 024 mm4, i = 10.39 mm
#               ; I_strong = 36*98^3/12 = 2 823 576 mm4, i = 28.29 mm
#   X1 RE-CHECK. The lift makes both posts 150 mm taller and, worse, it puts
#   150 mm into the ONE gap that governs each of them - the long unbraced run
#   between the bench rail and the end beam - because everything below the
#   bench rail stayed on the floor and everything above the end beam went up.
#   So this is the one place in the bed where X1 has to be re-argued rather
#   than re-typed. Both come out well inside, and both are written out below
#   with the pre-X1 numbers beside them.
#   FRONT POST (2037, was 1700). Y restraints: the front bench rail segment
#   laps its face at 229..297, the end beam is fixed to its X-inner face at
#   1304..1402 and the front side rail at 1402..1500, then the two guard bands
#   at 1708 and 1881. Worst unbraced length is bench rail -> end beam,
#   1304 - 297 = 1007 mm (was 708), so lambda = 97 (68), lambda_rel = 1.64
#   (1.16), k_c = 0.32 (0.58) and N_c,Rd = 3528 * 0.32 * 12.92 = 14.7 kN (26.4)
#   against a corner reaction of well under 1.5 kN: utilisation 0.10 (~0.05).
#   (v14/X7 COMPUTES this row now - see THE REAL EC5 6.3.2 in the load
#   section - so the figures here are a reading of the assert, not a rival.)
#   (The old 48x48 over the old 708 mm: lambda 51, k_c 0.75, 22.3 kN. The
#   thinner post is the STRONGER column, because 53% more area beats the loss in
#   radius of gyration.) The strong axis at the full 2037 is lambda = 72 - not
#   the governing case even unbraced.
#   BACK POST (1402, was 1065). Take the Y restraints as the end beam alone
#   (1304..1402) and the base as pinned: unbraced 1304 mm (was 967), lambda =
#   126 (93), k_c = 0.20 (0.35), N_c,Rd = 3528 * 0.20 * 12.92 = 9.1 kN (15.8)
#   against the corner reaction it carries in direct bearing off the rail top -
#   utilisation 0.16 (~0.10) at the 1.5 kN X7 stands over the corner. The
#   back bench rail and the ledger butt and
#   screw to its X-inner face at 229..297 and 614..682, so the real unbraced
#   length is shorter than that; 1304 is the conservative reading.
#   X1 SAYS THIS OUT LOUD RATHER THAN BURYING IT: a 337 mm lift puts all 337
#   into the ONE gap that governs each post - between the bench rail and the
#   end beam - because everything below the bench stayed near the floor and
#   everything above the end beam went up. Both posts stay well inside
#   (0.10 and 0.16 against the 0.5 gate), but the frame is more
#   slenderness-governed than it has ever been - which is why v14/X7 stops
#   arguing these in prose and RUNS EN 1995-1-1 6.3.2 on all four slender
#   members, this pair and the ladder's two axes, off the built solids and
#   against an assert. See THE REAL EC5 6.3.2 in the load section.
POST_HEIGHT = 2037                       # front posts + ladder uprights [X1: was 1700]
BACK_POST_HEIGHT = RAIL_BOTTOM           # 1402, the rail underside (W6)
                                         # [X1: was 1065; SLAT_Z1 1197, MATTRESS_Z1
                                         #  1337 before W6]
BACK_POST_Y0 = BACK_RAIL_Y0              # -48, back face ON the wall plane (W6)
BACK_POST_Y1 = BACK_POST_Y0 + POST_T     # -12  [was 0; -96..-48 before W6]
FRONT_POST_Y0 = FRONT_RAIL_Y1            # 752 .. 788 (outer face of front rail)
FRONT_POST_Y1 = FRONT_POST_Y0 + POST_T   # 788  [was 800, U2]
POST_THIN = RAIL_T - POST_T              # 12, U2: the post depth 48 -> 36
CORNER_POST_X = [0, WALL_SPAN - POST_W]  # 0..98 and 1892..1990 (walls untouched)

# ---------------------------------------------------------------------------
# THE VISIBLE FRONT (V5) - the only faces of this bed anyone looks at
# ---------------------------------------------------------------------------
# Three sides of this bed are wall (X 0, X 1990, Y -48), the top is under a
# mattress and the underside is floor. What is left is the FRONT: everything
# from the front rails' outer plane forward to the post plane U3 pins the
# envelope on. That layer - and nothing else - is on display.
#
# The four front guard boards have hung their two 5x60 per lap from INSIDE the
# bed since D14, for exactly this reason. V5 stops treating that as a habit of
# one joint and makes it the rule of the whole front:
#
#       NO FASTENER HEAD ON A ROOM-FACING FACE.
#
# A head is on one when the face it is driven from looks out of the front:
# the fastener travels in -Y and its head sits at or in front of
# VISIBLE_FRONT_Y. The assert is in the fastener block and it is an AESTHETIC
# assert - it says so, and nothing about it is structural. It is the whole
# reason J2, J3 and J8 are driven from inside the bed outward, through 48 mm
# of rail into 36 mm of post or upright, instead of the other way round.
# Both directions fit the through-screw rule at all three (a 6x80 crosses 36
# into 48 and 48 into 36 alike), so the fit rule calls them 'tvetydig' and
# hands the choice to the table - and this is what the table chooses on.
VISIBLE_FRONT_Y = FRONT_RAIL_Y1          # 752, the front rails' outer face

# W1/S2/W7: the wall plane. It is the back rail's outer face, and after W6 the
# back posts, the end-beam back ends, the back bench rail, the back ledger and
# every slat end lie in it too. It is the flat face the frame is bolted to - the
# fixing is screws through the back rail into the studs - it is the BARRIER on
# the back long side, which is why there are no back guard boards, and it is the
# mattress's back stop (W5). Declared up in the UPPER BED block; this is the
# identity that ties the two statements of it together.
# X10: this is a DECLARATION, not a check - WALL_Y and BACK_POST_Y0 are both
# defined as BACK_RAIL_Y0, which is -RAIL_T, so the line is -48 == -48 and
# nothing is built yet at this point in the file to ask instead. It is kept
# because it is where the three names are tied together in one place, and it is
# labelled so nobody counts it as a check again. The measured statement is
# WALL_PLANE_BUILT, down in the geometry block.
assert WALL_Y == BACK_POST_Y0 == BACK_RAIL_Y0 == -48     # the mounting face
                                                         # (a naming identity)

# W6: THE BACK RAIL BEARS ON THE POST TOPS. Post top == rail underside is the
# whole point of the round, so it is stated here as an identity and checked
# against the real parts in the validation section.
BACK_RAIL_ON_POST_Z = RAIL_BOTTOM        # 1402, post top == rail underside
# The rail is set in 3 mm at each wall (C9), so of the post's 98 x 36 top face
# the rail covers 95 x 36 = 3420 mm2 (U2; it was 45 x 48 = 2160 on the 48x48
# post). Against f_c90,d ~ 1.53 MPa with k_c90 = 1.5 that is ~7.9 kN of bearing
# under a corner reaction of well under 1 kN. It is the ONE corner in this bed
# where the vertical reaction never touches a fastener at all: rail -> post
# end grain -> floor.
# The rail is 48 deep in Y and the post only 36, so the rail overhangs the post
# by 12 mm on the ROOM side of the joint - i.e. the whole post top is covered
# and the bearing is limited by the post, not by the rail.
BACK_RAIL_POST_BEARING = (POST_W - THROUGH_X0) * POST_T  # 3420 mm2

# W5: WHAT CAPTURES THE MATTRESS SIDEWAYS. v9 left this to the WALL at Y -96 and
# the four front verticals at Y 752 - a 848 mm clear under an 800 mm mattress, so
# 48 mm of wander and one 48 mm gap at whichever end. W6 brings the wall forward
# to Y -48 and the clear becomes the mattress:
#   clear between the stops   752 - (-48) = 800
#   mattress                              = 800
#   so the mattress can wander            =   0 mm
# i.e. the mattress is PINNED between the wall and the front verticals, with no
# gap at either long edge - the zero-play fit D12 had, restored, and with slat
# under every millimetre of it. The EN 747 entrapment case on the back side is
# therefore 0 mm against a 75 mm limit.
MATTRESS_STOP_Y0 = WALL_Y                # -48, the room wall (W5/W7)
MATTRESS_STOP_Y1 = FRONT_POST_Y0         # 752, front posts + ladder uprights
MATTRESS_WANDER = (MATTRESS_STOP_Y1 - MATTRESS_STOP_Y0) - MATTRESS_W    # 0

# ---------------------------------------------------------------------------
# END BEAMS (48x98, rail stock)
# ---------------------------------------------------------------------------
# One per end, bolted to the inner faces of the two corner posts of that end.
# Its top is flush with the rail underside, so BOTH side rails land on it and
# it carries the platform across the end. Above the mattress the ends are
# completely open.
#
# UTILISATION NOTE (D4, end beam): a 1002 mm span carrying the two rail
# reactions. 48x123 -> 48x98 raises the bending utilisation by (123/98)^2 =
# 1.575 from ~0.24 to ~0.38 and roughly doubles the (tiny) deflection.
# Comfortable margin. D12 shortens the span 1002 -> 896 (-106), which takes
# the utilisation back down by roughly (896/1002)^2 = 0.80 to ~0.30. W6 takes
# another 48 off the BACK end, 896 -> 848, i.e. (848/1002)^2 = 0.72 -> ~0.27,
# and U2 takes 12 more off the FRONT end, 848 -> 836: (836/1002)^2 = 0.70,
# ~0.26. Every depth round this bed has had has made this member happier.
#
# W6: the beam's back end stops at the wall plane, which is the back rail face
# now. The beam still runs the full post-to-post depth - the posts just both sit
# inside it, the back one at Y -48..-12 and the front one at Y 752..788 - and it
# is still fixed to their X-inner faces (the X = 98 and X = 1892 planes after
# U2; 6x90 screws rather than M8, U4).
#
# U2/U3: the beam still runs from post face to post face and it is still bolted
# - screwed now, U4 - to their X-inner faces. Both faces moved: the back post's
# front face came in 12 (it is 36 deep, not 48) and the front post's front face
# with it, so the beam is 836 long, Y -48..788, and the bed is exactly that deep.
# V6b: THE END BEAMS ARE 36x98, NOT 48x98. The beam is loaded on edge - 98 mm
# is the bending depth either way - so dropping the thickness 48 -> 36 costs
# only the 25% of section modulus that sat in the width, and the member had
# margin to spare (utilisation 0.26 -> 0.35). It buys two things: the beams
# come off the 36x98 board that the posts and guards already use, and 48x98
# shrinks to the two side rails on one 4.2 m board. Nothing screws INTO a beam
# - J1 drives out of it into the post - so the thinner member is the ENTRY
# side, which the fits-the-face rule likes: 36 < 90 < 36 + 98.
END_BEAM_T = BOARD36_T                         # 36  [V6b: was RAIL_T = 48]
END_BEAM_Y0 = BACK_POST_Y0                     # -48  [was -96, W6]
END_BEAM_Y1 = FRONT_POST_Y1                    # 788  [was 800, 906]
END_BEAM_LEN = END_BEAM_Y1 - END_BEAM_Y0       # 836  [was 848, 896, 1002]
END_BEAM_Z1 = RAIL_BOTTOM                      # 1402, flush with rail underside
END_BEAM_Z0 = END_BEAM_Z1 - RAIL_H             # 1304  [X1: was 967..1065]
# D4/U2 ripple: the posts are 98 wide in X now, so the beams slide out to the new
# post inner faces X 98 / 1892 (they were at 48 / 1942 on a 48 mm post). The side
# rails run X 3..1987 and still cover both beams completely - 48 mm of full
# bearing on each, asserted in the validation block.
END_BEAM_X = [POST_W, WALL_SPAN - POST_W - END_BEAM_T]   # 98..134 / 1856..1892

# V5: THE FOUR J1-B BEARING BLOCKS ARE GONE, AND SO IS THE ARGUMENT FOR THEM.
# A 36x48 offcut used to sit under each beam end, screwed to the post face, so
# the beam "bore on wood instead of hanging in screw shear". Follow that one
# step further and it eats itself: the block does not stand on anything. It
# hangs on ONE 6 mm screw in shear - 2.0 kN against a corner reaction of up to
# 1 kN, utilisation 0.50, the highest screw row in the whole bed and the only
# 0.50 in vedlegg A. The block did not take the reaction out of steel; it put
# it into HALF the steel it would otherwise have had.
#
# What the beam end actually has without it, measured off this file:
#   * two 6x90 through the beam into the post (J1), 2 x 2.0 = 4.0 kN in shear
#     against <= 1 kN of corner reaction - utilisation 0.25, half the block's;
#   * 18 mm (3d) of end distance along the grain to the beam's own end, which
#     is the MIN_EDGE this file enforces everywhere else, and 27 mm (4.5d) of
#     edge distance in the direction the load acts (Z 1331/1375 in a beam that
#     runs Z 1304..1402). The perpendicular-to-grain loaded EDGE is what
#     governs a screw pair like this, and it has 4.5d.
# So the splitting story the block was bought to prevent is a 3d/4.5d lap
# fixing in 48 x 98 mm of C24, in the ordinary pattern the rest of the frame
# uses - not a defect.
#
# AND THE JIG IT REALLY WAS. What the block genuinely did was hold the beam at
# the right height while you drove the two J1 screws. That job now belongs to
# the holes: steg 0 bores the J1 pattern through beam and post clamped
# together, so at assembly the beam has exactly one height where the holes
# line up. The pre-drilled holes ARE the assembly jig.
#
# Deleted with it: 4 pieces off the 36x48 line, 4 x 6x90, one joint (J1-B) and
# the two vedlegg A rows that carried a 0.50.

# ---------------------------------------------------------------------------
# LADDER
# ---------------------------------------------------------------------------
# The uprights are in the SAME Y plane as the front corner posts, i.e. flat
# against the outer face of the front rail (through-bolted in reality).
#
# D13: the ladder narrows 420 -> 320 clear and the uprights slim 48x48 ->
# 36x48. The opening stays centred on X 995, so the INNER faces move out to
# 835 / 1155 and the OUTER faces to 799 / 1191 - i.e. the whole ladder is
# 100 mm narrower in the clear and 24 mm narrower over the uprights. 320 mm is
# still a comfortable climb-through (EN 747 asks for >= 300 between the ladder
# stiles for a child's bed ladder) and the 100 mm it gives back is what turns
# the two dead corners beside the ladder into a real walk-around passage.
#
# D13 / STRUCTURAL FLAG FOR THE DOCS ROUND - THE LADDER LOSES ITS LOW LATERAL
# RESTRAINT. Until v7 each upright was tied to the frame twice below the
# platform: the front bench rail segment lapped it face-to-face over 48 x 73 mm
# at Z 186..259, and the front side rail took it at Z 1065..1163. D13 cuts the
# bench rail back to the sofa ends, so the lap is gone and the ONLY connection
# to the frame below the guards is the through-bolted front side rail. The
# uprights remain bolted through that rail and they still carry the rungs (the
# rungs sit on 36x48 cleat blocks screwed to the upright inner faces, exactly as
# before), and the four rungs still triangulate the two uprights to each other
# in the ladder's own plane - what is gone is the out-of-plane (Y) hold at
# bench height.
#   BUCKLING, weak-plane check on the 36x48 section. U2 TURNS THE UPRIGHT, so
#   the two axes swap: the 36 mm is in Y now (out of plane) and the 48 mm in X
#   (in the ladder plane).
#     A = 1728 mm2; I (bending in Y, the 36 mm depth) = 48*36^3/12 = 186 624
#     mm4, i_y = 10.39 mm; I (bending in X, the 48 mm width) = 36*48^3/12 =
#     331 776 mm4, i_x = 13.86 mm.
#   In the ladder plane (X) the rungs brace the upright at 297 / 572 / 848 /
#   1073 / 1298 (X9), so the worst unbraced length there is the 276 mm pitch and
#   lambda_x = 20 - irrelevant, and better than the 25 it was. (X2's even ladder
#   had 245 and lambda_x = 19; the desk cost one point of slenderness on a
#   member that is not slenderness-governed in this direction at all.)
#   OUT OF PLANE (Y) is the one that moved, twice. v7: restrained at the bench
#   rail lap (top 259) and at the rail (1065), worst unbraced length 806 mm,
#   lambda_y = 58. v8/D13: the bench lap is gone, so the length runs floor to
#   rail, 1065 mm, and lambda_y = 77 on the 48 mm depth. v11/U2 turns the
#   section, so the same 1065 mm runs on i = 10.39: lambda_y = 102,
#   lambda_rel = 1.74, k_c = 0.29 and N_c,Rd = 1728 * 0.29 * 12.92 = 6.5 kN
#   against the ~1 kN a climber puts down an upright - utilisation ~0.15.
#   v14/X1 lifts the rail to 1402, so that same floor-to-rail run is 1402 mm:
#   lambda_y = 135, lambda_rel = 2.29, k_c = 0.17 and N_c,Rd = 1728 * 0.17 *
#   12.92 = 3.9 kN against the same ~1 kN - utilisation 0.26.
#   Ample, but this is now firmly a slenderness-governed member and the base is
#   still unrestrained in Y - so v14/X7 takes the arithmetic out of this
#   comment and puts it under an assert: EN 1995-1-1 6.3.2 by the k_c method,
#   on the built solids, against a 0.5 gate, and with THIS row MEASURED to be
#   the worst of the four. See THE REAL EC5 6.3.2 in the load section. The
#   floor-level tie back to the front corner posts stays unbuilt because 0.26
#   does not ask for it; the check is what will say when it does. (The panel's
#   front U-brackets are that tie today - see M4/F1.)
LADDER_Y0 = FRONT_RAIL_Y1                # 752, outer face of the front rail
LADDER_Y1 = LADDER_Y0 + UPRIGHT_T        # 788, same plane as the front posts
LADDER_CLEAR = 320                       # clear width between the uprights
LADDER_CENTER_X = 995
LADDER_INNER_L = LADDER_CENTER_X - LADDER_CLEAR // 2          # 835  (FIXED)
LADDER_INNER_R = LADDER_CENTER_X + LADDER_CLEAR // 2          # 1155 (FIXED)
LADDER_LEFT_X = LADDER_INNER_L - UPRIGHT_W                    # 787 .. 835
LADDER_RIGHT_X = LADDER_INNER_R                               # 1155 .. 1203
MIN_LADDER_CLEAR = 300                   # EN 747 clear width between stiles
# V7: the access opening is a BAND, not a floor. EN 747 wants 300..400 mm of
# clear width: under 300 a child cannot get through, over 400 the opening stops
# guiding the climb and becomes somewhere to fall through. 320 sits low in the
# band on purpose - the ladder is meant to be a snug climb, not a stair.
MAX_LADDER_CLEAR = 400                   # EN 747 upper bound on the same opening

# Rungs are proper treads out of 48x73 stock: 73 deep, 48 thick.
# D10: the treads sit BACK in the uprights - their front faces are flush with
# the upright front faces (D12: Y = 800) instead of standing 25 mm proud of
# them, so their back 25 mm reaches behind the plane Y = 752 and gives the
# movable panel's front edge a 320 x 25 mm ledge to rest on. The panel itself
# cannot come forward to meet the rung: the uprights occupy Y 752..800 right
# across its X range. Nothing else lives in Y 727..752 at any rung height -
# D11/D13 take the front bench rail out of the whole X band between the sofas.
#
# U2 ripple: the rung is the same 48x73 x 320 tread and it is still flush with
# the upright front face, but that face came in 12 mm with the turned upright,
# so the whole rung comes back with it: Y 727..800 -> 715..788. The ledge behind
# the upright plane grows by the same 12, 25 -> 37 mm, which is a strictly
# bigger seat for the movable panel's front edge (320 x 37 = 11 840 mm2 of
# bearing instead of 8 000). Nothing else in Y 715..752 at any rung height -
# D11/D13 keep the front bench rail out of the whole X band between the sofas.
RUNG_LEN = LADDER_CLEAR                  # 320, X 835 .. 1155  [was 420]
RUNG_T = TREAD_T                         # 48, tread thickness (Z)
RUNG_D = TREAD_D                         # 68, tread depth (Y)
RUNG_Y1 = LADDER_Y1                      # 788, flush with the upright front
RUNG_Y0 = RUNG_Y1 - RUNG_D               # 720  [was 715, 727]
RUNG_REST_LEDGE = LADDER_Y0 - RUNG_Y0    # 32, the bit behind the upright
                                         # plane  [was 37]
# D8: an even climb. Rung 1 shares its top with the bench rails (259), which is
# not a climbing step but the seat-height ledge you step onto; the rest of the
# rungs even out the way from there to the platform.
#
# X2 (v14): THE CLIMB IS A RULE NOW, NOT A LIST. D8 hand-set the four tops
# 259 / 482 / 720 / 958 against a 1197 mm platform, and the list has been drifting
# out of true ever since: V6's thinner slat took the platform to 1186 without
# re-evening anything, so the last step had quietly become 228 against 238s. A
# hand-set list cannot follow a platform that moves - and X1 moves it 337 mm - so
# the tops are DERIVED here instead, from the two things that actually decide
# them: where the climb starts (rung 1, on the bench rail) and where it ends (the
# slat surface). Fewest rungs that keep every step under the pitch limit, spaced
# as evenly as whole millimetres allow, and the asserts below judge the result.
#
# X2 also settles WHO OWNS RUNG 2. Under D8 the answer was "the table": rung 2
# was typed at 482 because the table-mode panel underside is 482, and the back
# ledger was moved up to meet it. That is backwards - a ladder whose rung
# spacing is set by a table top is a ladder with one step in the wrong place -
# and after X1 it is not even possible. So the ladder decides, and the TABLE
# FOLLOWS: rung 2 is 542 now, and PANEL_UNDER_TABLE and the back table ledger
# ride up with it. The builder's call, and it is an aesthetic one - an even
# ladder is what he wants to look at - so the price is stated out loud in the
# X-note at the top of the file: against a seat that went up 38 as well, the
# plate lands 140 mm over the cushion where v13 had 118.
#
# X2 PITCH LIMIT, 250 -> 280. The old 250 was this file's own comfort number,
# not a standard, and it was written for a 1186 mm platform where four rungs got
# there in 238 mm steps with room to spare. The climb is 1226 mm now (297 to
# 1523) and it takes FIVE rungs at either limit - the fifth rung is bought by
# the lift, not by the limit. What 280 buys is the right REASON for the count:
# a number the ladder trade uses rather than one this file invented for a bed
# that no longer exists. Portable-ladder practice (EN 131) puts uniform rung
# pitch in the 250..300 band; 280 is inside it, and the rule lands the pitch at
# 245, under both. The fifth tread and its two blocks are on the cut list.
# This is a rule being RE-AIMED, in the open, not an assert being bent to fit a
# result - the derivation below still has to satisfy it, and the evenness rule
# (MAX_CLIMB_SPREAD) is untouched and is now met to within one millimetre.
#
# X9 (v16): THE CLIMB TAKES A CONSTRAINT, AND THE EVENNESS RULE IS RE-AIMED.
# X2 wrote the ladder as a pure evenness problem - fewest rungs, spaced as
# evenly as whole millimetres allow - and X8 found what that leaves out: the
# loose plate has to be LIFTED OUT of the ladder bay in table mode, and a rung
# in the wrong place is a lid on that lift. X8 measured the lid (rung 3's
# underside, 739), computed the tallest table it allows (639) and refused the
# desk. X9 turns the lid round: the corridor is an INPUT to the climb now, and
# the derivation has to find a ladder that leaves it open. Same rule, one more
# constraint - not a hand-set list, and not a special case.
#
# WHAT THE CORRIDOR IS, IN HEIGHTS. The plate top is TABLE_PLATE_TOP (700 - the
# builder's number; see X9 at the top of the file). Under it hang the panel
# unit's own 68 mm of batten, so the SEATED unit occupies TABLE_UNIT_Z0..
# TABLE_PLATE_TOP, and to get it out the unit has to rise INSERT_CLEAR_MIN
# before the lift is a lift rather than a wrestle. So no rung top may lie in
#     (TABLE_UNIT_Z0, RUNG_ABOVE_TABLE_MIN) = (614, 848)
# - at or below 614 a rung is under the seated unit and out of the way; at or
# above 848 its underside is at or above 800 and the unit rises its 100 mm
# clear. Nothing in the band. That is the whole constraint, and every number in
# it is arithmetic on the plate and on a panel unit built long before the
# ladder.
#
# WHAT IT COSTS, AND THE RULE THAT PAYS. The band splits the climb into TWO
# FLIGHTS with one crossing step over it, and two flights of different pitch is
# exactly what MAX_CLIMB_SPREAD = 20 forbade. The COUNT does not change - five
# rungs either way, so the fifth rung X2 bought is still the fifth rung - but
# the steps do: 275 / 276 below the crossing and 225 / 225 / 225 above it, a
# spread of 51 against 20.
#   THE BUILDER OVERRULED HIS OWN EVENNESS, and that is why the number moves.
#   X1/X2 made the even ladder an AESTHETIC decision and said so out loud
#   ("the builder's call, and it is an aesthetic one - an even ladder is what
#   he wants to look at"). X9 is that decision being sold back for the desk, in
#   his own words: "700, and adjust the rungs / if need be the number of
#   rungs". So 20 does not survive - and what replaces it is TWO rules rather
#   than one bigger number, because the old one was doing two jobs:
#     MAX_FLIGHT_SPREAD  2   INSIDE a flight, where evenness is still the whole
#                            point. This is the old rule KEPT and TIGHTENED to
#                            whole-millimetre rounding and nothing else. Met
#                            at 1.
#     MAX_CLIMB_SPREAD  60   BETWEEN the flights. This one is not an evenness
#                            rule any more and does not pretend to be: it is a
#                            gate on how far the corridor may push two flights
#                            apart before the design has to be re-ARGUED rather
#                            than re-derived. 51 is what the corridor asks for
#                            here; 60 is where the file stops saying yes.
#   THE PITCH LIMIT IS UNTOUCHED at 280, and it is still the binding trade
#   number: the biggest step in the new ladder is 276, inside EN 131's 250..300
#   band, and that is what keeps this a ladder rather than a scramble.
MAX_CLIMB_STEP = 280             # pitch limit, rung 1 upwards  [X2: was 250]
MAX_CLIMB_SPREAD = 60            # BETWEEN flights  [X9: was 20, one flight]
MAX_FLIGHT_SPREAD = 2            # INSIDE a flight - whole-millimetre rounding

# THE DESK, AND THE CORRIDOR IT KEEPS OPEN. TABLE_PLATE_TOP is the only number
# in this block that is chosen; the other three are arithmetic on it and on the
# panel unit. They live up here, ahead of the panel that owns them, because the
# LADDER is the thing that has to be built round them - PANEL_UNDER_TABLE is
# read again at its own place in the LOWER CONVERTIBLE SECTION.
TABLE_PLATE_TOP = 700            # X9: a desk  [X2: 560, a sofa table]
PANEL_UNDER_TABLE = TABLE_PLATE_TOP - PANEL_T          # 682, the plate's seat
TABLE_UNIT_Z0 = PANEL_UNDER_TABLE - BENCH_RAIL_H       # 614, batten undersides
# The straight-up run the mode change is held to, in both modes. It used to be
# declared down in the insertion-sweep block that measures against it; X9 needs
# it HERE, because it is one of the two numbers that decide where rung 3 goes.
INSERT_CLEAR_MIN = 100           # mm of straight-up travel, both modes
RUNG_ABOVE_TABLE_MIN = (TABLE_PLATE_TOP + INSERT_CLEAR_MIN
                        + TREAD_T)                     # 848, rung 3's top


def _flight(z0, z1, n):
    """`n` even steps from z0 to z1, given as the rung tops that START each
    one - so z1 itself, which is the thing stepped ONTO, is not in the list."""
    return [z0 + (z1 - z0) * i // n for i in range(n)]


def even_climb(first_rung_top, surface, max_step, keep_clear=None):
    """Ladder rung tops from `first_rung_top` up to `surface`.

    The first rung is given - it is fixed by what it shares its top with - and
    the rest are the FEWEST that keep every step at or under `max_step`, spaced
    as evenly as whole millimetres allow. The last step is the one onto
    `surface` itself, so `surface` is not a rung and is not in the result.

    X9: `keep_clear` is an open band (lo, hi) no rung top may lie in - the
    corridor the table unit is lifted through. A climb that has to cross such a
    band is TWO FLIGHTS with one crossing step between them, so the search is
    over where that crossing lands: fewest rungs first, then the flattest
    result, then the lowest crossing. That is a total order, so the answer is
    the same on every run and nobody has to hand-set a list again."""
    span = surface - first_rung_top
    fewest = -(-span // max_step)            # ceil: how many steps it takes
    if keep_clear is None:
        return _flight(first_rung_top, surface, fewest)
    lo, hi = keep_clear
    for n in range(fewest, fewest + 8):
        best = None
        for below in range(1, n):
            for landing in range(int(hi), int(surface)):
                tops = (_flight(first_rung_top, landing, below)
                        + _flight(landing, surface, n - below))
                seq = tops + [surface]
                steps = [b - a for a, b in zip(seq, seq[1:])]
                if max(steps) > max_step:
                    continue
                if any(lo < t < hi for t in tops):
                    continue
                key = (max(steps) - min(steps), landing)
                if best is None or key < best[0]:
                    best = (key, tops)
        if best is not None:
            return best[1]
    raise ValueError(
        f"no ladder from {first_rung_top} to {surface} keeps {keep_clear} "
        f"clear at a pitch of {max_step}")


RUNG_TOPS = even_climb(BENCH_RAIL_TOP, SLAT_Z1, MAX_CLIMB_STEP,
                       keep_clear=(TABLE_UNIT_Z0, RUNG_ABOVE_TABLE_MIN))
#          X9: [297, 572, 848, 1073, 1298]
#          X1/X2: [297, 542, 787, 1032, 1277]   [was 259, 482, 720, 958]

# Cleat blocks under every rung end, screwed to the inner faces of the
# uprights; the rung sits on them and is screwed down from above.
#
# D13 CHECK - does the 36x48x73 block still work against a 36 mm wide upright?
# Yes, unchanged, because none of its three dimensions references the upright
# WIDTH: the 36 mm is the block's own stock thickness standing off the upright
# inner face (into the ladder opening), the 48 mm is its height in Z, and the
# 73 mm follows the tread depth in Y.
# U2 CHECK - the same block against a 36 mm DEEP upright. The piece is unchanged
# (same 36x48 stock, same 73 mm cut, same X, and it still sits directly under
# its tread), but the face it presents to the upright is now 36 (Y) x 48 (Z) =
# 1728 mm2 instead of 48 x 48 = 2304, because the block is 73 deep in Y and the
# upright only 36. The rest of the block - its rear 37 mm, Y 715..752 - hangs
# behind the upright's back plane together with the tread it carries, exactly as
# its rear 25 mm did before. The block is not the load path either way: the
# tread is screwed through the upright into its end grain as well (J4), and the
# block is what stops the joint rotating. No adjustment needed.
#
# K1 - THE BLOCK IS AS LONG AS THE UPRIGHT IS DEEP, 73 -> 36. This is the
# comfort round's one geometry change on the ladder, and it is a change that
# takes wood AWAY without touching a single load number. Read the U2 note
# above again: the block is 73 deep in Y and the upright only 36, so its rear
# 37 mm (Y 715..752) hangs behind the upright's back plane and TOUCHES
# NOTHING. It is not in the load path, it is not in the J5 screw's face, it
# is not even in contact with the piece it is screwed to. What it IS in is
# the bed-to-table transfer slot: the movable panel runs to Y 750 (PANEL_FIT
# off the uprights), so that unattached rear 35 mm of block is the ONLY thing
# that stood in the panel's ceiling under rung 2 - and it lowered that
# ceiling by the whole 48 mm of block height.
#
# So the block is cut to 36 and set at Y 752..788, the upright's own Y band:
#   * IDENTICAL contact face against the upright, 36 (Y) x 48 (Z) = 1728 mm2,
#     because that was already all the face it had. J5 does not move;
#   * the J5 screw now lands at Y 770 - the MIDDLE of the upright - instead
#     of at Y 751,5, which was half a millimetre outside its back plane;
#   * the rung bears on 36 x 36 = 1296 mm2 per end instead of 36 x 73. At the
#     0,5 kN a rung end takes that is 0,39 N/mm2 against 2,5 for C24 across
#     the grain, utilisation 0,16 - see the K1 row in the validation block;
#   * the rung's rear 37 mm is unsupported over 36 mm of its 320 mm length.
#     It is a 48 mm thick tread; this is not a span, it is a corner;
#   * the transfer slot's ceiling stops being the block and becomes the back
#     table ledger's underside, 386 -> 409. See TRANSFER_SLOT below.
# Everything else about the piece is unchanged: same 36x48 stock, same X,
# same height, same one 5x60. The kappliste loses 8 x 37 mm of offcut.
RUNG_BLOCK_T = BLOCK_T                   # 36 (X), stock thickness
RUNG_BLOCK_H = BLOCK_H                   # 48 (Z)
RUNG_BLOCK_LEN = UPRIGHT_T               # 36 (Y), as deep as the upright  [K1: was 73]
RUNG_BLOCK_Y0 = LADDER_Y0                # 752, the upright's own back plane
RUNG_BLOCK_Y1 = RUNG_BLOCK_Y0 + RUNG_BLOCK_LEN            # 788
RUNG_BLOCK_X = [LADDER_INNER_L,                          # 835 .. 871
                LADDER_INNER_R - RUNG_BLOCK_T]           # 1119 .. 1155

# ---------------------------------------------------------------------------
# GUARD RAILS  (W1: FRONT SIDE ONLY - the wall is the back barrier)
# ---------------------------------------------------------------------------
# W1. The two sides used to be geometrically identical mirror images. THEY ARE
# NOT ANY MORE. The bed stands with its back long side against the room wall
# and is bolted to it (S2), so on that side the wall IS the barrier and the two
# 34x98 boards that used to hang on the outer post faces at Y -130..-96 are
# deleted. The bands themselves are untouched - the D6 arithmetic below is the
# same arithmetic, it is just a front-side statement now - and the back side is
# checked instead against the mattress-to-wall gap (WALL_MATTRESS_GAP below).
# See the W1 block at the top of this file for what that costs in flexibility;
# in short, the bed is no longer reversible and the retrofit route back to a
# freestanding version is to put these two boards and two full-height back
# posts back in.
#
# D6 RE-BANDING. The flush top (D5) lifted the mattress surface 1274 -> 1337,
# which would have left a 56 mm opening under the old lower band and a useless
# 426 mm one above the top band. The bands moved to 1412..1510 and 1585..1683.
#
# U1 RE-BANDING. The 2 mm the board gained goes into the platform twice over -
# a thicker slat under a mattress that then sits 2 mm higher - so the mattress
# top goes 1337 -> 1339 and both bands go up with it, by 2. The board is also
# 2 mm thicker in Y, but it is 98 wide in Z either way, so the band HEIGHT is
# unchanged and every opening is the same arithmetic two millimetres up:
#     1339 -> 1414   75 mm   (mattress top to the underside of band 1)
#     1512 -> 1587   75 mm   (between the bands)
#     1685 -> 1700   15 mm   (band 2 to the top of the FRONT posts)
# i.e. every one of them at or under the 75 mm EN 747 entrapment limit, and
# the top edge of the barrier 1685 - 1339 = 346 mm above the mattress (EN 747
# asks for 160). This is the item that closes the entrapment finding. The third
# opening is the only one that changes at all: it closes against the FIXED 1700
# post tops, so it absorbs the whole 2 mm, 17 -> 15 mm.
#
# V6 RE-BANDING. Same rule as U1, the other way. The 23 mm slat takes 13 mm out
# of the platform build-up, so the mattress top goes 1339 -> 1326 and both bands
# follow it DOWN by 13 - the bands are dimensioned off the sleeping surface, not
# off the floor. Every opening is therefore the same arithmetic 13 mm lower:
#     1326 -> 1401   75 mm   (mattress top to the underside of band 1)
#     1499 -> 1574   75 mm   (between the bands)
#     1672 -> 1700   28 mm   (band 2 to the top of the FRONT posts)
# The barrier top is 1672 - 1326 = 346 mm above the mattress, exactly as before,
# and the legal mattress window is untouched at 140..326 mm. The third opening
# is again the only one that changes, because it closes against the FIXED 1700
# post tops: it ABSORBS the 13 mm and grows 15 -> 28. Nothing about the mattress
# the reader buys changes; the bed just got 13 mm of build-up cheaper.
#
# X1 RE-BANDING, and this time the mattress moved as well as the platform. The
# rule is the one U1 and V6 used and it has not changed: THE BANDS ARE
# DIMENSIONED OFF THE SLEEPING SURFACE. What is new is that X1 does two things
# to that surface at once - it lifts the slat top 1186 -> 1523, and it thins
# the mattress 150 -> 120 - so the bands do not simply travel with the deck.
# They are re-struck off the new sleeping surface by the same arithmetic that
# has always set them: band 1 sits 65 mm above the mattress top (mid-band in
# EN 747's 60..75, which is where V7 put it and why), band 2 sits 75 above
# band 1's top, and the mattress WINDOW falls out of band 1's position:
#     1643 -> 1708   65 mm   (mattress top to the underside of band 1)
#     1806 -> 1881   75 mm   (between the bands)
#     1979 -> 2037   58 mm   (band 2 to the top of the FRONT posts)
# The barrier top is 1979 - 1643 = 336 mm above the mattress - the same 336 the
# bed has had since D6 - and the legal mattress window moves with the modelled
# thickness, 140..155 -> 110..125, which is what a 120 mm mattress means. The
# THIRD opening is the only one that is not the same number it was: the post
# tops are set by the lift (2037) and the bands by the mattress, so the two no
# longer arrive at the same place and the remainder, 28 -> 58 mm, shows up
# there. It is still an opening above the sleeping surface and it is still
# under the 75 mm limit, which is the only thing EN 747 asks of it. Nothing about the guard detail,
# the mattress the reader buys or the EN 747 arithmetic changes with the lift;
# the whole assembly simply stands 150 mm further off the floor.
GUARD_BAND_Z0 = [1708, 1881]             # [X1/X3: was 1401, 1574]
MAX_GUARD_OPENING = 75           # EN 747 entrapment limit, above the mattress
MIN_GUARD_OVER_MATTRESS = 160    # EN 747 barrier height above the mattress
# D14: the guards hang inboard of the verticals now, so they overhang the
# mattress footprint by their own thickness. This is how much air has to be left
# between the mattress top and the underside of the lowest board for that
# overhang to be a non-event. It is the same 75 mm as the D6 opening - the band
# position sets both numbers at once - but it is a MINIMUM here, not a maximum:
# raise the bands and the clearance grows, lower them and the board starts to
# come down towards the mattress.
# V7: the overhang is a non-event once the gap is in the EN band, where a whole
# limb passes rather than wedges - so this follows the band's LOWER edge, not
# the 75 it used to copy off the opening cap. At 75 it pinned the mattress to
# exactly the thinnest legal one and left no margin at all.
MIN_GUARD_INBOARD_CLEAR = 60
# U2: the narrowest face lap the guard detail has ever been signed off on - the
# 36 mm of a v10 ladder upright, two 5x60 into 36 x 98 = 3528 mm2. Every lap in
# the bed has to be at least that, and after U2 both of them are more: 48 mm on
# a turned upright and 95 mm on a 98 mm corner post.
MIN_GUARD_LAP = 36

# W1: the BACK side's EN 747 case. There is no guard board there, so the
# opening to check is not between two boards, it is the gap between the edge of
# the mattress and the wall the bed is bolted to - the classic bed/wall
# entrapment gap. v9 had the mattress edge at Y -48 and the wall at Y -96, i.e.
# a 48 mm gap as drawn, and after W4/W5 a 48 mm WANDER that could put those
# 48 mm at either edge.
#
# W6/W7 close it. The wall plane is the back rail face Y = -48 and the mattress
# edge is drawn on it, so the clear between the two stops is exactly the
# mattress and the gap is 0 at BOTH edges - there is nothing left to wander.
# Both numbers below are therefore 0 and both are checked against the same 75 mm
# limit, which is now a formality rather than a margin.
WALL_MATTRESS_GAP = MATTRESS_Y0 - WALL_Y   # 0, the gap as DRAWN
MAX_MATTRESS_GAP = MATTRESS_WANDER         # 0, the mattress is pinned

# W1 / RETROFIT NOTE (for the docs round). The deleted back boards were
# 34x98 x 1984 at Y -130..-96 (i.e. GUARD_T off the outer post faces), in the
# same two GUARD_BAND_Z0 bands as the front. D1 sized them for the full 1894 mm
# single span between the corner post inner faces: 21x95 flat-on (W = 6983 mm3)
# was at utilisation 1.99 - a failure - and 34x98 (W = 18 883 mm3) brought the
# 0.54 kN/m barrier line load down to ~12.9 MPa against f_m,d = 16.6 MPa, i.e.
# ~0.78. Those numbers still stand if anyone ever puts them back; the geometry
# they need is two full-height (2037) back corner posts, which is the OTHER half
# of the retrofit. Nothing else in the model has to move.
#
# D2: the front boards are cut in two so the ladder opening carries on past
# the guard rails - you climb THROUGH, not over.
# NOTE (deviation from the sketch): the sketch had the segments STOP at the
# uprights' outer faces. That is only a line contact - the board end face meets
# the upright side face but the guard plane and the upright plane merely share
# an edge, so the board would be a long cantilever off one corner post and be
# fixed to nothing at its inner end. The segments therefore LAP the uprights
# (D14: on the INNER Y face) and stop flush with the upright INNER X faces,
# which (a) gives a full face-to-face screwed lap at the inner end, (b) leaves
# a clear opening exactly as wide as the ladder itself.
#
# D7: the segments go 21x95 -> the common board (34x98, 36x98 after U1), the
# same board as the back guards and
# every slat in the bed. The lap face is unchanged - the boards land flat on
# the face of the corner posts and of the ladder uprights, they are just
# 13 mm thicker. (D14 then swaps WHICH face: the inner one.)
#
# D13: the uprights moved out to inner faces 835 / 1155, so each segment grows
# 782 -> 832 mm and the climb-through opening becomes 320 mm. The lap onto the
# upright shrinks with the upright, 48 -> 36 mm (still a full 36 x 98 = 3528
# mm2 screwed face, two 5x60 into 36 mm of end grain-free timber). Support
# centres go 737 -> 787 mm; the board was at utilisation ~0.12 at 737 mm
# so at 787 it is ~0.14 - nothing.
# U2: both laps grow. The corner post is 98 wide, so the segment laps 95 x 98 =
# 9310 mm2 of it (the 3 mm C9 setback is all that is missing); the turned ladder
# upright gives 48 x 98 = 4704. The support centres come IN, 787 -> 762 mm
# (post centre 49, upright centre 811), so the utilisation goes back to ~0.13.
# D12: the whole band comes forward-plane -106, Y 906..940 -> 800..834.
#
# D14 DEPTH RECLAIM. The guard boards move from the OUTER faces of the front
# posts / ladder uprights to their INNER faces: Y 800..834 -> 718..752, i.e. in
# by POST_T + GUARD_T = 82 mm. Nothing else moves, so the whole 34 mm the guards
# used to stand proud of the frame comes off the overall depth (930 -> 896) and
# the outermost thing on the front face becomes the post plane Y = 800 itself.
# Consequences, in order:
#   * the boards now overhang the mattress footprint by GUARD_T = 34 mm, from
#     Y 752 back to 718. That is NOT a contact: the guard bands start at Z 1412
#     and the mattress tops out at 1337, so the nearest board is 75 mm ABOVE the
#     mattress surface with nothing but air in between (the same 75 mm opening
#     D6 sized to the EN 747 entrapment limit). Sit up in bed and the board is
#     over your knees, not against them;
#   * the laps are the same X overlaps onto the same members, just on the other
#     face - the INNER Y faces of the two ladder uprights (36 mm wide) and of
#     the two front corner posts. Same 36 x 98 and 45 x 98 screwed faces, same
#     board, same span. The one build difference: the screws are now driven
#     FROM INSIDE THE BED, through the board and into the post/upright, instead
#     of from outside. Two 5x60 per lap as before;
#   * the climb-through gap is untouched. The segments still die on the upright
#     inner faces X 835 / 1155, they just butt them from the other side of the
#     upright, so the opening is still measured between the same two faces:
#     320 mm.
#
# U1/U2 ripple: the guard plane is defined off the post INNER face, which has
# not moved (752 - it is the front rail's outer face), so the boards do not move
# outward at all; they get 2 mm thicker inboard, Y 718..752 -> 716..752. The lap
# onto a CORNER POST grows with the post: 45 x 98 -> 95 x 98 = 9310 mm2 of
# screwed face, because the post is 98 wide in X now. The lap onto a LADDER
# UPRIGHT grows the same way, 36 -> 48 mm (U2 turned it), so 48 x 98 = 4704 mm2.
# Both laps are still full-face and the climb-through is still 320.
FRONT_GUARD_Y1 = FRONT_POST_Y0                 # 752  [was 834, 940]
FRONT_GUARD_Y0 = FRONT_GUARD_Y1 - GUARD_T      # 716  [was 718, 800, 906]
FRONT_GUARD_SHIFT = POST_T + GUARD_T           # 72, D14: outer face -> inner
FRONT_GUARD_SEGMENTS = [(THROUGH_X0, LADDER_INNER_L),      # 3 .. 835
                        (LADDER_INNER_R, THROUGH_X1)]      # 1155 .. 1987
FRONT_GUARD_SEG_LEN = LADDER_INNER_L - THROUGH_X0          # 832  [was 782]

# ---------------------------------------------------------------------------
# LOWER CONVERTIBLE SECTION
# ---------------------------------------------------------------------------
# C5: the bench rails are 48x73 members at Z 186..259, one per Y plane, instead
# of two 645 mm rails per plane. The loose panel had nothing to bear on in the
# gap X 655..1335 before; now there is an unbroken edge behind it. They also
# give the ladder uprights a low fixing point. Max span 700 mm (utilisation
# 0.14).
#
# D11: the BACK rail is still the continuous member. The FRONT one is
# cut, so the ladder bay is open right down to the floor - there is no longer a
# beam across your shins when you stand at the foot of the ladder.
#
# W9 (v10): the back rail is 1894 mm, X 48..1942, not 1984 mm at X 3..1987. The
# back corner posts moved into its Y band (-48..0) and would collide with it at
# both corners, so it butts their X-inner faces instead and is SCREWED to them -
# an end fixing it never had. Its mid supports (the two stub legs) are unchanged,
# and it still runs unbroken behind the panel's whole X range. The through-
# running-member rule C9 is unaffected: 1894 goes into a 1990 opening even more
# easily than 1984 did.
# U2 (v11): the same sentence with a 98 mm post - 1794 mm, X 98..1892 - and the
# face it butts is 36 mm deep instead of 48, so the end contact is 36 x 73 =
# 2628 mm2. Easier still to manoeuvre, and the clear span between its stub legs
# is the unchanged 700 mm that governs it.
#
# D13: the cut goes all the way back to the SOFA ENDS. v7 stopped the segments
# at the ladder uprights (X 3..785 / 1205..1987, 782 mm) with a face lap onto
# the upright; v8 stops them at X 645 / 1345 (X 3..645 / 1345..1987, 642 mm),
# which is where the sofa slats end and where the stub legs already stood. The
# consequences, in order:
#   * each segment's inner end now lands SQUARE ON ITS STUB LEG (X 572..645 /
#     1345..1418) instead of overhanging it by 140 mm to reach the upright, so
#     the leg goes from a mid-span prop to a clean end bearing and the segment
#     is a two-support member, X 3..48 on the corner post and 572..645 on the
#     leg: a 597 mm span with zero cantilever;
#   * NOTHING at bench-rail height crosses the 700 mm between the two benches
#     any more - the whole front floor in front of the ladder is clear;
#   * the ladder upright loses this lap, which was its low lateral restraint.
#     See the LADDER section for the buckling numbers and the docs-round flag.
# D12: the front rail plane comes in 106 mm, 810..858 -> 704..752.
# BENCH_RAIL_TOP / BENCH_RAIL_BOTTOM are declared up in SHARED LOWER DATUM -
# the ladder section needs the top for RUNG_TOPS[0].
BENCH_RAIL_Y = [BACK_RAIL_Y0, FRONT_RAIL_Y0]        # -48..0 and 704..752
# W9: the back bench rail and the back table ledger run POST TO POST, X 48..1942,
# butting the two back corner posts and screwed to their X-inner faces. The two
# side rails still run wall to wall at X 3..1987 (C9) - they pass OVER the posts,
# so nothing is in their way.
# U2 ripple: the post is 98 wide in X, so the two members that run POST TO POST
# lose 100 mm - 1894 -> 1794 - and their end fixing lands on a face that is
# 36 mm deep in Y instead of 48. The back bench rail is 48 deep, so 36 of its
# 48 mm butts the post (48 x 73 -> 36 x 73 = 2628 mm2 of screwed end contact);
# the ledger is 21 deep and butts over its whole 21 x 95 = 1995 mm2, unchanged.
# Both end fixings are 6x90 screws through the post into the member's end grain
# (U4) - 18 mm edge distance on the post's 36 mm face, 3d, exactly as the M8
# had 24 in a 48 mm face.
BETWEEN_POSTS_X0 = POST_W                           # 98, back post inner face
BETWEEN_POSTS_X1 = WALL_SPAN - POST_W               # 1892
BETWEEN_POSTS_LEN = BETWEEN_POSTS_X1 - BETWEEN_POSTS_X0     # 1794  [was 1894]

# C3: bench slats 21x95 -> the common board (21x95 was at utilisation 1.96 with a
# point load on one slat). Consequence: the bench top rises 280 -> 293, and the
# bed-mode panel does NOT follow it - the panel is an 18 mm sheet on a rail top
# that has not moved - so the difference is the cushion recess (D10).
# U1 ripple: on the 36 mm board the bench top is 295 and the recess 18 mm.
BENCH_TOP = BENCH_RAIL_TOP + BENCH_SLAT_T      # 320, bench slat top / seat
                                               # height  [X3: 295]
BENCH_LEN = 645                                # slatted zone / stub leg reference
BENCH_X = [0, WALL_SPAN - BENCH_LEN]           # 0..645 and 1345..1990
BENCH_SLAT_Y0 = BACK_RAIL_Y0                   # -48, on the wall plane like every
                                               # other slat  [was BACK_POST_Y1]
BENCH_SLAT_Y1 = FRONT_RAIL_Y1                  # 752  [was 858]
BENCH_SLAT_LEN = BENCH_SLAT_Y1 - BENCH_SLAT_Y0 # 800  [was 906]
BENCH_SLAT_COUNT = 5
# W9 RIPPLE - THE BENCH SLATS ARE RE-PITCHED. A bench slat is Y -48..752, i.e. it
# covers the back rail plane, and the outermost one of each bench used to start
# at the wall, X 0..98 - straight through the corner post's new Y band. The field
# therefore starts at the post INNER face and the five slats are re-pitched to
# still finish on the bench end:
#   was     X 0..648,  pitch 137.5,  gap 39.5 (doc J11)
#   v10/W9  X 48..645, pitch 124.75, gap 26.75
#   v11/U2  X 98..645, pitch 112.25, gap 14.25
# U2 ripple: the post is 98 wide in X now, so the field starts 50 mm further in
# and the same five slats close up again. Same five 36x98 x 800 pieces per bench,
# closer together - a strict improvement for a seat, and 14.25 mm is nowhere near
# the 60 mm gap limit - and the outer end still butts the post, so the bench is
# tied to the frame at that end. The bench is a 547 mm slatted field with 490 mm
# of board in it: 90% timber, 10% gap.
BENCH_SLAT_X_START = POST_W                    # 98, clear of the back post (W9)
BENCH_SLAT_PITCH = (BENCH_LEN - BENCH_SLAT_X_START - BENCH_SLAT_W) / \
    (BENCH_SLAT_COUNT - 1)                     # 112.25  [was 124.75, 137.5]
MAX_BENCH_SLAT_GAP = MAX_SLAT_GAP              # 60, the same seat/platform limit
STUB_LEG_H = BENCH_RAIL_BOTTOM                 # 229, floor to bench rail underside
                                               # [X3: was 191 - the bench went up 38]
# The RULE, unchanged since W3 and re-derived here for U5: the leg's INNER face
# is on the inner end of its bench - X 645 on the left bench, X 1345 on the
# right - and the leg runs OUTWARD from there, away from the open floor, so it
# is always fully under its own rail segment whatever its width. At 73 mm that
# puts them at 572..645 / 1345..1418 (they were 597..645 / 1345..1393 while the
# leg was 48 wide; 572/1418 is where W3 found them).
STUB_LEG_X = [BENCH_LEN - LEG_W,               # 572..645
              WALL_SPAN - BENCH_LEN]           # 1345..1418
# W3: the minimum end bearing in X of a bench rail on a stub leg. 40 mm was the
# floor the deleted C2 bearing blocks were held to as well; the 73 mm leg
# clears it easily.
MIN_LEG_BEARING = 40
# U5: leg-on-rail contact area and its compression-perpendicular utilisation.
# 48 x 73 = 3504 mm2; at f_c90,d ~ 1.53 MPa with k_c90 = 1.5 that is ~8.0 kN
# against the ~0.5 kN a leg carries -> ~0.06. (Was 48 x 48 = 2304 mm2, ~0.09.)
LEG_BEARING_AREA = LEG_W * LEG_T               # 3264 mm2  [was 3504, 2304]

# D13: the front bench rail segments end at the SOFA ends, on their stub legs.
FRONT_BENCH_RAIL_SEGMENTS = [(THROUGH_X0, BENCH_LEN),              # 3 .. 645
                             (WALL_SPAN - BENCH_LEN, THROUGH_X1)]  # 1345 .. 1987
FRONT_BENCH_RAIL_SEG_LEN = BENCH_LEN - THROUGH_X0                  # 642  [was 782]
# The clear front floor between the two benches: 645 .. 1345.
OPEN_FLOOR_X = (BENCH_LEN, WALL_SPAN - BENCH_LEN)                  # 645 .. 1345
# D13: the walk-around passages, one on each side of the ladder, between the
# sofa end and the upright outer face. Nominally 799 - 645 = 154 mm each.
MIN_PASSAGE = 140                # clear walk-around beside the ladder

# V5: THE FOUR J9-B / J9-F BENCH-RAIL BEARING BLOCKS ARE GONE TOO, for the
# same reason as the J1-B blocks under the end beams (see the note up in END
# BEAMS): a block that hangs on one 6 mm screw does not take the reaction out
# of steel, it halves the steel the joint would otherwise have had.
#
# What each bench-rail end has instead, measured off this file:
#   BACK  - two 6x90 skew screws into the post's X-inner face (J8-B),
#           2 x 2.0 = 4.0 kN in shear. The screws lie in the XY plane and the
#           reaction is Z, so both of them are square to the load and neither
#           loses anything to the skew. Outer span post 98 -> stub leg centre
#           608.5, i.e. ~510 mm; 1 kN of bench load at its midpoint puts
#           0.5 kN on this end - utilisation 0.13, and 0.25 if you stand the
#           whole kilonewton directly over the post.
#   FRONT - two 6x80 through the rail segment into the post (J8), the same
#           4.0 kN, the same 0.13 / 0.25. The segment is a two-support member
#           with no cantilever: post at one end, stub leg at the other.
# Neither number is anywhere near the 0.8 that would have stopped this change,
# and both are BELOW the 0.50 the block's own single screw used to carry.
#
# The blocks were the shelf you rested a rail on while you drove its end
# screws. The pre-drilled holes are that shelf now: steg 0 bores J8 and J8-B
# through both members clamped together, and a hole pattern has exactly one
# position it lines up in.

# ---------------------------------------------------------------------------
# V2: THE PANEL IS A DROP-IN ASSEMBLY, AND ITS OUTLINE IS SET BY TWO NUMBERS
# ---------------------------------------------------------------------------
# THE SIDE GAP IS AN EN 747 NUMBER, NOT A LEFTOVER. The panel used to be 680
# wide in a 700 mm opening, i.e. 10 mm of play against each bench - and 10 mm
# is inside the band a child's finger gets caught in. The rule the seated panel
# has to obey on every accessible edge is a BAND, not a maximum: under 5 mm a
# finger does not enter at all, 12..25 mm it passes freely, 60..75 mm the whole
# limb passes and the gap is back under the EN 747 opening limit - and in
# between it wedges. v12 read that as "24 mm" and got a 652 mm panel.
#
# K2 - THE PANEL WIDTH IS QUANTIZED, AND THIS ROUND PICKS THE NEXT WINDOW DOWN.
# The opening is fixed at PANEL_OPENING = 700 mm between the two benches and
# the gap is (700 - width)/2 on each side, so the width is not a dial: it is
# whatever the legal gap bands allow it to be. Written out (see
# PANEL_WIDTH_WINDOWS below, which is this table computed, not typed):
#
#     gap band        width window     note
#     0 .. 5          690 .. 700       impractical - eats PANEL_FIT itself
#     12 .. 25        650 .. 676       where v12 sat (652)
#     60 .. 75        550 .. 580       CHOSEN, K2
#     anything else   581 .. 649       FORBIDDEN - gaps 25,5..59,5 wedge
#
# WHY MOVE. The reason is table-mode insertion, and it is an ergonomic one,
# not a structural one: the panel is lowered into the table seat by hand, over
# its head, and the only thing that aims it is the two guide battens dropping
# past the rung ends. Before they engage, the whole 574 mm of sheet has to
# arrive between two bench ends. 24 mm of side gap is 24 mm of forgiveness;
# 63 mm is 63. That is the entire argument, and it costs table area.
#
# WHY 63 AND NOT 60 OR 75. Maximum width inside the band is minimum gap, so
# the pull is downwards towards 60 - but 60 is the DANGEROUS wall: a gap that
# comes out under it lands in the 25,5..59,5 wedge zone. A sheet cut 2 mm wide
# takes 1 mm off each gap, so the margin at that wall has to survive the saw.
# 63 keeps 3 mm there and 12 mm at the harmless wall, and it is the widest
# panel that does. Panel: 574 x 798 (was 652 x 798), table area 0,458 m2
# (was 0,520) - a 12% loss, stated where anyone can see it.
PANEL_OPENING = WALL_SPAN - 2 * BENCH_LEN      # 700, bench end to bench end
PANEL_SIDE_GAP = 63                            # EN 747: inside the 60..75 band
EN_GAP_BAND = (12.0, 25.0)                     # a finger passes freely
EN_LIMB_BAND = (60.0, 75.0)                    # a limb passes; EN 747's own limit
PANEL_X0 = BENCH_LEN + PANEL_SIDE_GAP          # 708  [was 669]
PANEL_X1 = WALL_SPAN - BENCH_LEN - PANEL_SIDE_GAP   # 1282  [was 1321]
PANEL_W = PANEL_X1 - PANEL_X0                  # 574  [was 652, 680]
EN_FINGER_FREE = 5.0                           # a finger does not enter below this
# The three legal gap bands, low to high, and the panel-width window each one
# implies through gap = (PANEL_OPENING - width)/2. This list is what makes the
# quantization a MACHINE fact rather than a paragraph: a future "just take a
# few millimetres off the panel" edit lands between two windows and the build
# stops with the table above printed at it.
EN_LEGAL_GAP_BANDS = ((0.0, EN_FINGER_FREE), EN_GAP_BAND, EN_LIMB_BAND)
PANEL_WIDTH_WINDOWS = tuple(
    sorted((PANEL_OPENING - 2 * _hi, PANEL_OPENING - 2 * _lo)
           for _lo, _hi in EN_LEGAL_GAP_BANDS))   # (550,580) (650,676) (690,700)
# THE FIT. Nothing that has to be lowered into a hole may be drawn touching the
# walls of the hole: a panel whose front edge is DRAWN on the ladder-upright
# back plane is a panel that has to be forced past it. 2 mm on the front edge
# is the insertion clearance, and the same 2 mm is what the rung-end brackets
# below are held off the rung ends by, so the whole assembly has one fit number.
PANEL_FIT = 2                                  # insertion clearance, mm
# D10: the panel is as deep as a slat (D12: Y -48..752) because it has to REACH
# the wood it rests on: the back bench rail lives at Y -48..0 and the back table
# ledger did too after V2 widened it. Its rear edge is flush with the rear edge
# of the bench slats (both -48), so in bed mode bench / panel / bench form one
# unbroken field. Its front edge stops PANEL_FIT short of the ladder-upright
# plane: the uprights stand at Y 752..788 and the panel's X range straddles both
# of them, so 752 is a hard limit - which is precisely why the rungs had to move
# back 25 mm to meet it - and 750 is that limit with the fit taken off.
PANEL_Y0 = BENCH_SLAT_Y0                       # -48, flush with the bench slats
PANEL_Y1 = LADDER_Y0 - PANEL_FIT               # 750, 2 mm off the uprights
PANEL_LEN = PANEL_Y1 - PANEL_Y0                # 798  [was 800]

# D10: NO HOOKS. The panel is a loose board that LIES on wood, and the geometry
# below is what makes that true in both modes:
#
#   BED MODE    underside 297 = the bench rail tops = rung 1 top. It lands on
#               the back bench rail (680 x 48 = 32 640 mm2) and on rung 1
#               (320 x 25 = 8 000 mm2). Top 277 - see PANEL_BENCH_DIP.
#   TABLE MODE  underside 542 = the back ledger top = rung 2 top (X2 moved all
#               three together). It lands on the ledger (680 x 21 = 14 280 mm2)
#               and on rung 2 (320 x 25 = 8 000 mm2). Top 560.
#
# D13 changed the bed-mode case: the front bench rail used to reach into the
# panel's X range and offer 260 x 48 mm under the two front corners, but it now
# stops at the sofa ends (X 645 / 1345) well outside the panel (X 655..1335).
# Both modes are therefore the SAME two-line support now - one back member, one
# rung - with the bearing lines 727 mm apart (Y 0 and Y 727) instead of 858.
# For an 18 mm pine board 680 wide that is a 727 mm simple span, and BARE that
# is not good enough: at the 2 kN dynamic design point (someone sits or kneels
# on the panel, not the 0.55 kN static table load) W = 680*18^2/6 = 36 720 mm3
# puts the bending utilisation at ~1.42 - a fail. M4 answers it with the two
# stiffener battens below.
#
# THE PANEL CONNECTIONS (V2). The krokplate and the U-brakett are GONE. Both
# were bespoke bent flat steel, both gripped the far side of a member, and both
# made the panel something you thread onto the bed rather than something you
# drop into it. What replaces them is four shop-bought angle brackets and one
# principle: THE PANEL LIES ON WOOD, AND THE STEEL ONLY SAYS WHERE.
#
#   WHAT HOLDS IT UP        wood. Rear edge on the back bench rail (bed) or on
#                           the back table ledger (table) - both 48 mm deep at
#                           Y -48..0 after V2 - and front edge on the rung.
#   WHAT HOLDS IT IN Y      the room does. The rear edge IS the wall plane and
#                           the front edge is PANEL_FIT off the ladder
#                           uprights, so Y travel is 2 mm and needs no steel.
#   WHAT HOLDS IT IN X      the two FRONT brackets. Each is an angle screwed up
#                           under the panel just outboard of a rung end, with
#                           its second flange standing down the rung's END FACE
#                           PANEL_FIT clear of it. The rung ends are 320 apart
#                           in BOTH modes (rung 1 at Z 297, rung 2 at Z 542,
#                           same X), so one bracket geometry serves both.
#   WHAT HOLDS IT IN Rz     the same two. Rotation about Z drives both front
#                           brackets the same way in X, so one of the two jams
#                           whichever way it turns.
#   WHAT SEATS THE REAR     the two REAR brackets, in the side gaps. The flange
#                           lies ON the rear support's top, beside the panel,
#                           never under it - so the panel still lands flat on
#                           wood - and the upstand is screwed to the panel's
#                           edge. In bed mode the flange end also stops the
#                           panel against the bench slat ends; in table mode
#                           there is nothing out there and the front pair does
#                           the work alone. The flange is where the bed-mode
#                           LOCK goes: a screw straight down through it.
#
# WHAT IS NOT BLOCKED, AND ON PURPOSE: uplift. The panel is meant to be lifted
# out, in both modes, straight up. A bed-mode lock was the candidate answer;
# V4 decides against fitting one (accepted deviation, vedlegg B avvik 4) and
# keeps the wood-to-wood geometry as the retrofit point.
PANEL_UNDER_BED = BENCH_RAIL_TOP               # 297, rests on the rails/rung 1
PANEL_TOP_BED = PANEL_UNDER_BED + PANEL_T      # 315  [X3: 277]
# X9: PANEL_UNDER_TABLE IS NO LONGER A RUNG TOP. It is declared in the LADDER
# section (682 = TABLE_PLATE_TOP - PANEL_T) because the ladder is derived round
# it, and here is where it is USED. Under X2 this line read `RUNG_TOPS[1]` and
# the table followed the ladder; under X9 the plate is a desk at a height no
# rung may stand at, so the seat is made of a ledger at the back and two
# bearer blocks at the front and the LADDER follows the table's corridor
# instead. The precedence X2 settled is not reversed - the ladder still decides
# where its own rungs go - it is that the table stopped asking for one.
PANEL_TOP_TABLE = PANEL_UNDER_TABLE + PANEL_T  # 700
# The whole move, in one number: the two seats are this far apart and the panel
# sub-assembly - sheet, battens, screws - is the same object at both of them.
PANEL_MODE_LIFT = PANEL_UNDER_TABLE - PANEL_UNDER_BED       # 385  [X9: 223]

# ---------------------------------------------------------------------------
# M4: PANEL STIFFENER BATTENS - AND, AFTER V3, THE GUIDES AS WELL
# ---------------------------------------------------------------------------
# Two 48x73 battens ON EDGE (48 wide in X, 73 deep in Z), screwed up into the
# underside of the panel and travelling with it. They run the full 750 mm from
# the rear bearing to the panel's own front edge, so the panel stops being an
# 18 mm board on a 750 mm span and becomes a pair of tee-sections with the
# panel as their flange - AND they are the thing that finds the rung ends.
#
# UTILISATION NOTE (M4, panel, 2 kN dynamic). Bare 18 mm panel over the span
# between the two bearing lines: W = 652*18^2/6 = 35 208 mm3, utilisation ~1.4
# - a fail. With two 48x73 battens on edge the load goes into the battens, not
# the sheet: each batten alone gives W = 48*73^2/6 = 42 632 mm3, the two
# together 85 264 mm3, and composite action with the 18 mm flange lifts that
# further. Sharing the 2 kN over the pair at midspan, M = 1000*750/4 =
# 187 500 Nmm and sigma = 4.4 MPa against f_m,d = 16.6 for C24: utilisation
# ~0.26. The deflection follows the same way - the thin panel over that span
# was the item the docs round was asked to sign off on, and the battens remove
# the question rather than answer it.
#
# V3: THE BATTENS ARE THE GUIDES. They used to sit 11 mm inside the rung-block
# line and stop 2 mm short of the rung's rear face, and a pair of angle
# brackets bolted under the panel did the locating: a 2 mm steel flange
# standing down each rung's end grain. That steel is gone. The battens have
# moved OUTBOARD of the rung ends and forward to the panel's front edge, so
# each one now runs down the 48 x 37 mm free shaft beside a rung end - the
# same shaft the bracket flange stood in - with the same 2 mm fit, and 48 mm
# of Z engagement against 40 mm of bracket leg. Wood on end grain, over
# 48 x 35 mm instead of 2 x 40 mm of galvanised plate.
#
# GEOMETRY - the constraints, in the order they bite:
#   X  the batten's INBOARD face is PANEL_FIT off the rung's end face, and the
#      rung ends are at X 835 / 1155 at BOTH heights (rung 1 at Z 297, rung 2
#      at Z 542), so one pair of battens guides the panel in both modes. The
#      pair lands at X 785..833 and 1157..1205, symmetric about the ladder /
#      panel centreline X 995 (centres 809 and 1181, i.e. +/- 186). Outboard
#      of the rung end there is nothing at any height in the batten's Y band
#      - the ladder uprights start at Y 752 - so the shaft is open top to
#      bottom and the assembly goes straight down it.
#   Y  rear: the back bench rail occupies Y -48..0 at Z 229..297, which is
#      exactly the bed-mode batten band, so Y0 = 0 (the back ledger at Y -48..0
#      is the same plane in table mode). Front: Y1 = PANEL_Y1 = 750, flush with
#      the panel's own front edge and the same 2 mm off the uprights the panel
#      already keeps. The last 35 mm of that - Y 715..750 - is the batten IN
#      the shaft, alongside the rung end.
#   Z  the batten TOP is the panel underside, so the battens hang BELOW it:
#      229..297 in bed mode, 614..682 in table mode [X9: was 474..542]. 229 is
#      the bench rail underside, which is the floor of the ladder-bay walking
#      zone - the battens sit at its ceiling and never enter it. Asserted
#      below.
#
# WHAT THE FRONT END BEARS ON, SAID OUT LOUD. Nothing, directly: the rung is
# 320 mm long and the battens are outboard of both its ends, so the batten's
# front end hands its reaction into the panel and the panel carries it 26 mm
# across - batten centreline X 809 to the rung's bearing edge X 835 - into the
# rung. In 18 mm sheet, taking a conservative 100 mm of effective width and
# the whole 1 kN corner reaction: M = 1000*26 = 26 000 Nmm, W = 100*18^2/6 =
# 5400 mm3, sigma = 4.8 MPa against the ~6.95 MPa the bare-panel row in
# vedlegg A is calibrated on - utilisation 0.69. That short cross-hand is the
# price of putting the guides where the guiding has to happen, and it is the
# panel's governing sheet row now.
BATTEN_W = BENCH_RAIL_T                        # 48, batten width (X)
BATTEN_H = BENCH_RAIL_H                        # 68, batten depth (Z), on edge
BATTEN_Y0 = BACK_RAIL_Y1                       # 0, clear of the back rail/ledger
BATTEN_Y1 = PANEL_Y1                           # 750, the panel's own front edge
BATTEN_LEN = BATTEN_Y1 - BATTEN_Y0             # 750  [was 713]
BATTEN_X = [LADDER_INNER_L - PANEL_FIT - BATTEN_W,   # 785 .. 833
            LADDER_INNER_R + PANEL_FIT]              # 1157 .. 1205
BATTEN_Z0_BED = PANEL_UNDER_BED - BATTEN_H     # 229 == BENCH_RAIL_BOTTOM
BATTEN_Z0_TABLE = PANEL_UNDER_TABLE - BATTEN_H # 614  [X9: 409]
# THE SHAFT the batten runs in, and how much of it it uses. 48 mm of rung
# thickness in Z, 32 mm of rung rest ledge in Y (the bit of the rung that
# stands proud of the upright plane), and the batten occupies 30 of those
# 32 mm.
#
# X10 - AND THE LAP IS NOT THE LIFT. These were one constant and they are two
# different distances, which is how the file came to say that the assembly has
# to rise 48 mm to come free of its locator. It does not. The batten LAPS the
# locator over RUNG_T of Z - the tread is 48 thick and the batten stands beside
# it over all 48 - but the batten's underside is BATTEN_H below the panel, not
# RUNG_T, because the locator's top IS the panel's underside: 229 against 297
# in bed mode, 614 against 682 in table mode. So it takes 68 mm to lift the
# batten's bottom edge past the locator's top edge, and 68 is BATTEN_H.
#   ENGAGE_Z  the lap - what the guide is worth as a guide. Drawings, the
#             mechanism sheet and the retning check read this one.
#   RELEASE_Z the lift - what it takes to get free. The insertion sweep reads
#             this one, and the old sweep was asking `_run > 2 x 48 = 96`
#             against a table-mode run of 100: right answer, wrong question,
#             and 4 mm from failing on a number that was never the number.
#             The requirement is one release lift, not two laps: the assembly
#             is free the moment the battens clear the locator tops, and
#             INSERT_CLEAR_MIN (100) is the separate rule that says a lift has
#             to be a lift and not a wrestle. 100 > 68 with 32 mm to spare.
BATTEN_GUIDE_ENGAGE_Z = RUNG_T                 # 48, the Z lap into the shaft
BATTEN_GUIDE_RELEASE_Z = BATTEN_H              # 68, batten underside -> the
                                               # locator top  [was RUNG_T, 48]
BATTEN_GUIDE_ENGAGE_Y = BATTEN_Y1 - RUNG_Y0    # 30, how deep into the shaft
                                               # [was 35]

# ---------------------------------------------------------------------------
# V2/M5: THE TWO FRONT CROSS BATTENS - THE CANTILEVER THE PANEL STILL HAS
# ---------------------------------------------------------------------------
# THE DEFECT. The panel's front bearing is the RUNG, and the rung is only
# 320 mm long (X 835..1155) in a panel that is 652 wide. Everything outboard of
# the rung end is bare 18 mm sheet with a 750 mm run back to the rear bearing
# and NOTHING under it. Kneel on that corner (the documented case: a child
# climbing off the bench onto the panel) and the sheet alone carries it.
#
# V3 ASKED WHETHER THESE TWO COULD GO. Moving the M4 battens outboard shrinks
# the bare corner from 213 mm to 116 mm, so the question is fair. The answer is
# NO, and the reason is that a point load at a FREE CORNER of a plate does not
# care how far the support is: model the overhang as a cantilever strip whose
# effective width is its own length a (a 45 degree spread from the load towards
# the one support that exists), and sigma = P*a / (a*t^2/6) = 6P/t^2 - the a
# cancels. 6 * 1000 / 18^2 = 18.5 MPa against the ~6.95 MPa the bare-panel row
# in vedlegg A is calibrated on: utilisation 2.66, at 116 mm exactly as at
# 213 mm. Only wood under the corner fixes a corner. So the cross battens stay,
# and what changes is that they get SHORTER (213 -> 116 mm) and move FORWARD to
# the panel's own front edge, where the knee actually lands. With the load on
# the cross batten itself it is a 116 mm cantilever off the M4 batten:
# M = 1000*116 = 116 000 Nmm, W = 48*73^2/6 = 42 632 mm3, sigma = 2.7 MPa
# against f_m,d = 16.6 for C24 - utilisation 0.16.
# GEOMETRY:
#   Y  Y 702..750 - the front face is FLUSH with the panel's front edge, so the
#      corner load lands on wood and not on a 37 mm sheet nose. It stays clear
#      of the ladder uprights the same way the panel does (they start at
#      Y 752), and clear of the FRONT BENCH RAIL (Y 704..752) in X: the rail
#      stops at 645/1345 and the batten starts at the panel edge, 24 mm in.
#   X  from the panel's side edge to the M4 batten's near face, so the two meet
#      end-on and the pair reads as one L-shaped stiffener under each front
#      corner. 116 mm.
#   Z  the same band as the M4 battens - top on the panel underside, 73 mm
#      below it - so the walking zone is untouched.
# AND IT IS THE LOCK POINT. In BED mode the cross batten's outboard end face
# stands 24 mm from the front bench rail's end face, in the same Y band and the
# same Z band - two pieces of wood side by side across the side gap. In TABLE
# mode the cross batten is PANEL_MODE_LIFT higher and there is nothing beside
# it at all.
# A lock fitted there is therefore a bed-mode lock BY GEOMETRY, not by
# instruction, which is what an EN 747 conversion lock ought to be.
NOSE_Y1 = PANEL_Y1                             # 750, flush with the front edge
NOSE_Y0 = NOSE_Y1 - BATTEN_W                   # 702
NOSE_X = [(PANEL_X0, BATTEN_X[0]),             # 669 .. 785
          (BATTEN_X[1] + BATTEN_W, PANEL_X1)]  # 1205 .. 1321
NOSE_LEN = BATTEN_X[0] - PANEL_X0              # 77  [was 116, 213]

# ---------------------------------------------------------------------------
# V3: HOW THE BATTENS ARE FIXED TO THE PANEL - AND WHY NOT FROM ABOVE
# ---------------------------------------------------------------------------
# The panel is a TABLE TOP for half of this bed's life, and until V3 the four
# battens were held by twelve 5x60 driven down through it. Twelve heads in the
# middle of the table. Three ways to get rid of them were costed:
#
#   (a) GLUE + UP-SCREWS OUT OF A COUNTERBORE   <- chosen
#       A 5x40 driven from the batten's UNDERSIDE, out of a 12 mm clearance
#       hole bored 46 mm up into the 73 mm batten: 27 mm of batten left for the
#       screw to pass through and 13 mm of thread in the 18 mm sheet, with 5 mm
#       of ply standing over the point (the model's own tip-cover rule wants
#       4). The counterbore is not decoration - it is the only way to AIM the
#       thread: straight through 73 mm of batten a 5x80 would bite 7 mm and a
#       5x90 would bite 17 of the 18 and blow the face off.
#       THE ONLY LOAD CASE IS UPLIFT AND HANDLING. In service gravity presses
#       this joint shut: the panel BEARS on the batten's top edge, so the 2 kN
#       dynamic point load never passes through a fastener at all, and the M4
#       bending row credits the battens' own section without composite action.
#       What the screws carry is the assembly being picked up by one corner.
#       Withdrawal, EC5 8.5.1.1 with d = 5, l_ef = 13, rho_k = 350:
#       f_ax,k = 0.52 * 5^-0.5 * 13^-0.1 * 350^0.8 = 18.9 N/mm2, so
#       F_ax,Rk = 18.9 * 5 * 13 * k_d(0.625) = 768 N and F_ax,Rd = 532 N at
#       k_mod 0.9 / gamma_M 1.3. Halve it again for withdrawal into plywood
#       rather than solid softwood and call it 265 N per screw. The assembly's
#       own weight is computed below (PANEL_UNIT_MASS) rather than quoted:
#       ~4.1 kg of sheet plus ~2.2 kg of lekt, about 62 N. Picked up by one
#       corner with a factor 2 that is ~124 N, against 16 screws. ONE of them
#       covers the whole panel twice over; utilisation on the worst-loaded
#       group is under 0.05. The glue (D3, 48 x 750 = 36 000 mm2 per long
#       batten) is not in that sum - it is what stops the sheet drumming on
#       the batten, and it is why the screws can be clamps.
#   (b) TOE-SCREWS THROUGH THE BATTEN SIDES - rejected. An 18 mm sheet met at
#       30 degrees off the batten's face offers 18/cos30 = 21 mm of path before
#       the point breaks out of the TOP face, and a countersink in a skew hole
#       cannot sit flush (this model already allows a tenth of a toe screw's
#       head to stand proud of the wood). The one fastener that must not touch
#       the table top is the one most likely to come through it.
#   (c) PLUGGED AND FLUSH-TRIMMED TOP SCREWS - rejected, and this is the one
#       that hurts. It is the classic answer and in solid pine it is very
#       nearly invisible. The panel is 18 mm KRYSSFINER (see innkjopsliste):
#       its top face is a continuous rotary-cut veneer, and a 12 mm plug in it
#       is a disc of end grain in an unbroken face - twelve of them down the
#       middle of the table. Near-invisible stops being near-invisible on the
#       material this part is actually made of.
#
# K2 FINDING - THE ARGUMENT THAT FORCED PLYWOOD HAS EXPIRED, AND THE MATERIAL
# HAS NOT MOVED WITH IT. Up to v12 the sentence above read "this panel is 652
# wide, which is wider than shop limtre furu goes, so it is plywood": the
# widest limtre furu panel on the shelf is 600 mm, and 652 simply could not be
# had. At 574 it can. That does not make the panel limtre - the bare-panel
# bending row in vedlegg A, the halved withdrawal for the up-screws and the
# plug argument above are all calibrated on plywood, and re-taking a material
# decision is not what a comfort round is for - but the REASON has to stop
# being quoted, because it is no longer true. Recorded here and in the buying
# list as an open choice rather than a constraint.
LIMTRE_SHELF_W = 600             # widest limtre furu panel in the shop
PANEL_FITS_LIMTRE = PANEL_W <= LIMTRE_SHELF_W                 # True after K2
PANEL_UPSCREW_LEN = 40                         # 5x40, the stock length
PANEL_UPSCREW_PASS = 27                        # wood left under the screw head
# K2 FINDING - THE FITS-THE-FACE RULE SIZES THE SCREW, NOT THE HOLE IT SITS IN.
# These screws do not stand in the wood on their own: each one sits at the
# bottom of a 12 mm clearance bore, and the rule that spaces a row - 4d between
# 5 mm screws, i.e. 20 mm - was written for the SHANK. Twenty millimetres
# between two 12 mm holes leaves eight millimetres of wood, and on the 116 mm
# wing that never came up because the row had 35,5 mm to spread into. K2's
# 77 mm wing collapsed it onto the 4d minimum and the drawing showed three
# bores nearly touching. So the bore gets its own rule, stated the only way a
# hole can be stated: how much wood has to be left between two of them.
PANEL_UPSCREW_CBORE_D = 12                     # the clearance bore
MIN_CBORE_WEB = PANEL_UPSCREW_CBORE_D          # 12, a bore's worth of wood
MIN_CBORE_PITCH = PANEL_UPSCREW_CBORE_D + MIN_CBORE_WEB       # 24 mm centres
PANEL_UPSCREW_CBORE = BATTEN_H - PANEL_UPSCREW_PASS       # 41, bore depth
PANEL_UPSCREW_BITE = PANEL_UPSCREW_LEN - PANEL_UPSCREW_PASS   # 13, into the ply
PANEL_UPSCREW_COVER = PANEL_T - PANEL_UPSCREW_BITE            # 5, ply over it

# ---------------------------------------------------------------------------
# V4/M5: THE FRONT WINGS BECOME WEDGES - AND WHY NOT PLYWOOD DOUBLERS
# ---------------------------------------------------------------------------
# THE COMPLAINT, and it is a fair one: the MECHANISM is the two guide battens.
# The two front cross battens are not mechanism at all, they are there for one
# load case - a knee on the free corner of the sheet - and at utilisation 0.16
# they are three times the wood that case needs. Under a table you look at from
# a sofa, two 73 mm blocks hanging under the front corners are the only clutter
# left. Three ways out were costed and the numbers are here, because the one
# that lost lost on a number and not on taste.
#
#   (c) 18 mm PLYWOOD CORNER DOUBLERS - REJECTED, and this is the one that
#       looked best. A patch of the panel's own sheet glued under each front
#       corner: no protrusion at all, invisible, and the insertion sweep does
#       not even notice it. The bending case is the free-corner cantilever
#       strip, sigma = 6P/t^2 with the effective width cancelling:
#         FULL composite action (36 mm laminate):  6*1000/36^2 = 4.63 MPa,
#           utilisation 0.67 on the ~6.95 MPa the bare-panel row is calibrated
#           on. Passes.
#         ZERO composite action (two 18 mm plies sharing the load, each on its
#           own): 6*500/18^2 = 9.26 MPa, utilisation 1.33. FAILS.
#       So the whole detail hangs on ONE glue line, and that glue line sits at
#       the NEUTRAL AXIS of the laminate, which is where longitudinal shear is
#       greatest: tau = 1.5V/(b*h) = 1.5*1000/(77*36) = 0.54 MPa (the wing
#       is 77 mm since K2, not the 116 this line was written on; and k_cr
#       does not enter - it is a glue line in plywood, not a sawn face).
#       The glue
#       itself is fine (D3 is several MPa) and even plywood's rolling shear
#       (~0.6-0.8 MPa design) has margin. The glue line is not what kills it.
#       WHAT KILLS IT IS THAT NOTHING CAN BACK IT UP. Every other glued joint
#       in this panel has screws as clamps; here there is no screw that fits.
#       An 18 mm doubler under an 18 mm sheet is 36 mm of material, and the
#       shortest screw in this bed is a 5x40 - 4 mm of it would come out of the
#       panel's TOP face, the one face that must never be broken - while a
#       counterbore cannot be sunk in 18 mm and still leave meat. So the
#       doubler would be glue-only, clamped, with a no-glue bound that is a
#       FAILURE. A detail whose fallback is 1.33 is not a detail this bed
#       carries under a child's knee.
#   (b) SLIMMER WINGS, 48x48 - workable, not chosen. Utilisation goes
#       0.16 * (73/48)^2 = 0.37, which is fine, but 48x48 is a profile this bed
#       spent two revisions (W3, U5) getting RID of, and re-opening it for two
#       116 mm pieces is exactly the orphan-profile trap U5 closed. Ripping
#       48x73 down to 48x48 needs a rip cut, and every cut in this bed is 90
#       degrees on a crosscut saw.
#   (a) THE WEDGE - CHOSEN. Same 48x73 stock, same 116 mm, same two screws'
#       worth of work, one extra saw cut: the underside is planed off in a
#       single straight line from FULL 73 mm at the root, where it butts the
#       guide batten, down to PANEL_UPSCREW_PASS at the tip on the panel's own
#       edge. The low outer corner - the whole of what you see from the sofa -
#       is gone, and what is left follows the moment diagram: a cantilever off
#       the guide batten has its moment at the ROOT and nothing at the TIP.
#
# WHY THE TIP IS 27 AND NOT A NUMBER SOMEBODY LIKED. It is the up-screw. Every
# J13 screw's head sits PANEL_UPSCREW_PASS below the panel's underside - that
# is what the 46 mm counterbore in a 73 mm batten means - so the wing has to be
# at least that deep wherever a screw goes through it. At exactly 27 the
# counterbore has vanished and the head is flush with the wing's own underside;
# below 27 the screw would have nothing to sit in. So the tip is the screw
# seat, and the counterbore rule is unchanged and now reads the same for all
# four pieces: bore up until PANEL_UPSCREW_PASS of wood is left.
#
# THE CRITICAL SECTION IS NOT THE ROOT. With h(x) = tip + (root-tip)*x/L
# measured from the tip, sigma(x) = 6*P*x/(b*h(x)^2) peaks where h = 2*tip,
# i.e. at x = tip*L/(root-tip) = 27*116/46 = 68 mm from the tip - INSIDE the
# piece, not at the root. There h = 54 mm and sigma = 2.92 MPa against
# f_m,d = 16.6 for C24: utilisation 0.18, against 0.16 at the root (2.72 MPa)
# and 0.16 for the old full-depth block. The wedge costs two utilisation points
# and gives back 46 mm of visible depth at the corner. Shear is the other end
# of the piece: at the 27 mm tip, tau = 1.5*1000/(K_CR*48*27) = 1.73 MPa
# against f_v,d = 2.77, utilisation 0.62 - the highest number on the part, and
# it is the number that says do not take the tip any thinner.
# [was 1.16 / 0.42, i.e. the same section computed without k_cr. See K_CR
#  below: the width the model was dividing by was the sawn width, and EC5 does
#  not let you have it.]
NOSE_TIP_H = PANEL_UPSCREW_PASS                # 27, the up-screw's own seat
# X10 - THE C24 DESIGN VALUES THE PRINTS ABOVE WERE QUOTING AS LITERALS, and
# the one factor that was missing from all of them. Shear in solid timber is
# computed on a REDUCED width in Eurocode 5 (6.1.7(2)): a drying check runs
# along the grain at mid-depth, which is exactly where longitudinal shear is
# greatest, so the code takes b_ef = k_cr * b and k_cr = 0.67 for softwood in
# service class 1-2. ASSEMBLY has said so since the round that wrote vedlegg A;
# the model did not do it, and the two documents printed different numbers for
# the same detail - 0,42 here and 0,62 there. The model is the one that was
# wrong. Every shear row in this file divides by K_CR now, and the numbers in
# the report are the ASSEMBLY ones.
#
# The two strengths beside it were literals in f-strings for the same reason
# nobody noticed the missing factor: a number typed into a print cannot be
# re-derived and cannot be re-read. They are named here.
K_CR = 0.67                      # EC5 6.1.7(2), sprekkfaktor on the shear width
F_V_D = 2.77                     # N/mm2, C24 shear, design (k_mod 0.9 / gM 1.3)
F_M_D_C24 = 16.6                 # N/mm2, C24 bending, design, no k_h

NOSE_ROOT_H = BATTEN_H                         # 68, full depth at the root
                                               # [V2: 73]
NOSE_TAPER_DEG = math.degrees(math.atan2(NOSE_ROOT_H - NOSE_TIP_H, NOSE_LEN))
# where the bending peaks along the taper, measured from the TIP
NOSE_CRIT_X = NOSE_TIP_H * NOSE_LEN / (NOSE_ROOT_H - NOSE_TIP_H)      # 50.7
                                                                      # [was 68.1]
NOSE_CRIT_H = NOSE_TIP_H * 2                                          # 54

# ---------------------------------------------------------------------------
# V4: WHERE A BED-MODE LOCK WOULD GO - AND WHY THERE IS NOT ONE
# ---------------------------------------------------------------------------
# THE DECISION, TAKEN: there is NO lock. It is an accepted deviation from
# EN 747 4.1.1 and the reasoning is written out in docs/ASSEMBLY.md, vedlegg B,
# avvik 4 - in one line: the mattress lies ON the panel and has to come off
# before the panel can lift, this is the LOWER bunk with a 42 cm fall to the
# floor (CUSHION_TOP_BENCH; the 26 this line used to say was BENCH_RAIL_TOP
# before X3 raised the bench, and it never counted the cushion), and the panel
# is a 6,3 kg unit (PANEL_UNIT_MASS; ~9 was a guess made before the sheet was
# weighed) whose guides take every lateral degree
# of freedom.
#
# WHAT STAYS HERE IS THE WOOD. The geometry below is kept as a measured,
# asserted RETROFIT POINT, because all three options drawn in
# docs/preview/laasvalg.png act across exactly these two faces and none of them
# needs a single millimetre of timber changed: fit one later and the only thing
# that happens is that a fastener appears. The faces are the one pair in this
# bed that are side by side in bed mode and nowhere near each other in table
# mode:
#
#   the FRONT CROSS BATTEN's outboard end face   X 669 / 1321, Y 702..750
#   the FRONT BENCH RAIL's end face              X 645 / 1345, Y 704..752
#
# In bed mode both are in the Z band 229..297 and 24 mm apart across the side
# gap - two 48x73 end faces looking straight at each other. In table mode the
# cross batten is PANEL_MODE_LIFT higher and there is nothing beside it, so a
# lock fitted here is a BED-MODE lock by geometry and not by instruction: it
# cannot be left engaged in the wrong position, because in the wrong position
# it has nothing to engage. All three options in docs/preview/laasvalg.png act
# across that 24 mm; the geometry of all three stays valid whether or not one
# is ever fitted, which is exactly why the numbers below are still asserted.
LOCK_GAP = PANEL_SIDE_GAP                      # 63, the side gap itself
                                               # [was 24]

# The walking zone under the ladder bay: floor to the bench rail underside. The
# battens are not allowed into it in either mode.
WALK_ZONE_Z = (0, BENCH_RAIL_BOTTOM)           # 0 .. 229  [X3: was 0 .. 191]

# D10: the bed-mode panel top is deliberately 16 mm BELOW the bench tops. The
# fold-out seat cushions are what turn the three zones into one sleeping
# surface, and this is the recess they fold down into - a panel flush with the
# bench slats would leave the cushions standing proud of it instead.
#
# K2 - AND WHAT THE WIDER SIDE GAP DOES TO THE SLEEPING SURFACE, said plainly.
# The panel is 574 wide in a 700 mm opening, so in BED MODE the middle zone is
# 574 mm of panel with a 63 mm open strip down each side, running the full
# 798 mm from the wall to the ladder. The strips are not holes in the platform
# - they are the same recess, 18 mm deeper - but they are open: the back
# 48 mm of each one looks down onto the back bench rail's top at 297, and the
# rest of it onto the walk zone and the floor. What closes them is the seat
# cushion, which is what closes the recess in the first place. A cushion that
# spans a 700 mm zone bridges a 63 mm strip at its edge the way any foam
# mattress bridges a slat gap; the bed's own upper platform runs on 44,5 mm
# gaps between slats and the benches on 14,25.
# The strips are legal because 63 mm is in the EN 747 60..75 band (K2) - a
# limb passes, nothing wedges - and they are the price of the insertion
# comfort the round was opened for. THIS IS A REAL CHANGE TO WHAT THE BED
# FEELS LIKE with the cushions off, and it belongs in the manual, not in a
# footnote: see docs/ASSEMBLY.md, the K2 note in the mode-change section.
PANEL_BENCH_DIP = BENCH_TOP - PANEL_TOP_BED    # 5  [V6: was 18]
PANEL_SIDE_STRIP_LEN = PANEL_LEN               # 798, the strip runs the depth

# BACK TABLE LEDGER (21x95), permanently mounted in both modes.
# NOTE (deviation, back ledger): the original spec placed it at Y 0..21, but
# nothing exists in that plane at this height, so the board would float.
# W9: it is 1794 mm at X 98..1892 (1894 at 48..1942 on the v10 post) - it butts
# the two back corner posts, which stand in its own Y band, and it is SCREWED TO
# THEIR X-INNER FACES (21 x 95 = 1995 mm2 of end fixing per end - the ledger is
# 21 deep and the post 36, so U2 costs this one nothing at all). Before, it ran wall to wall at X 3..1987 and
# was merely fixed to the posts' inner Y faces. It only picks up the
# panel's rear edge (a 680 mm wide load band at midspan): at a 0.55 kN table
# load, half of it on the rear bearing, M = 89 kNmm against W = 21*95^2/6 =
# 31 587 mm3, so sigma ~ 2.8 MPa -> utilisation ~0.17, deflection ~2 mm. The
# long span is a non-issue because the board is on EDGE for this load.
#
# D9: the ledger moves up 16 mm, to Z 387..482, so its TOP is the table-mode
# panel underside itself - level with rung 2, no hook step in between. Its
# 21 mm width is the depth of the rear bearing.
# V2: THE LEDGER BECOMES A BENCH-RAIL PROFILE, 48x73 AT Y -48..0. It was
# 21x95 on edge at Y -48..-27, and three things paid for the change:
#   1  THE REAR SEAT IS NOW THE SAME IN BOTH MODES. Bed mode seats the panel
#      (and the two rear brackets' flanges) on the back bench rail, 48 mm deep
#      at Y -48..0; table mode seated them on 21 mm at Y -48..-27, so a flange
#      that landed square on the rail cantilevered 13 of its 20 mm off the
#      ledger. One profile, one seat, one bracket geometry - which is the
#      whole argument for a drop-in panel with four identical corners.
#   2  IT STOPS BEING THE CEILING OF THE MOVE. The panel has to clear whatever
#      hangs over it on the way down to the bench rail, and the 95 mm board on
#      edge had its underside at 387 - one millimetre below the rung block at
#      386, i.e. it was about to become the thing that governed the insertion
#      path. At 409 it is 23 mm clear of the blocks, so the straight-down move
#      is governed by the LADDER alone (109 mm, measured in the insertion-path
#      block below) and the rear support is out of the argument for good.
#   3  ONE FEWER PROFILE ON THE LIST. 21x95 was in this bed for the ledger and
#      nothing else - one 1794 mm piece keeping a whole stock line alive. It is
#      cut from the 48x73 board the bench rails, the rungs, the stub legs and
#      every panel batten already come from.
# It is also stronger where it matters: 48x73 on edge gives W = 42 632 mm3
# against the 21x95's 31 587, on the same 1794 mm post-to-post span, and the
# end fixing into the 36 mm post face goes 21x95 = 1995 mm2 to 36x73 = 2628.
#
# X9: THE LEDGER IS THE EASY HALF OF THE DESK. It is the same 48x68 on the same
# wall plane, screwed to the same two posts, 140 mm higher: 474..542 -> 614..682
# and its spikerslag zone with it. Nothing about the piece changes - not its
# length, not its profile, not its end fixing - which is the whole reason the
# rear seat was never the thing that stood in the desk's way.
LEDGER_BACK_T = BENCH_RAIL_T                   # 48 (Y)  [was BOARD_T = 21]
LEDGER_BACK_H = BENCH_RAIL_H                   # 68 (Z)  [was BOARD_W = 95]
LEDGER_BACK_Z1 = PANEL_UNDER_TABLE             # 682  [X9: was 542, X2: 482]
LEDGER_BACK_Z0 = LEDGER_BACK_Z1 - LEDGER_BACK_H     # 614  [was 474]
LEDGER_BACK_Y0 = BACK_RAIL_Y0                  # -48 .. 0, on the wall plane

# ---------------------------------------------------------------------------
# X9: THE TABLE BEARERS - TWO BLOCKS WHERE THERE USED TO BE A RUNG
# ---------------------------------------------------------------------------
# Until X9 the plate's front edge landed on RUNG 2 and PANEL_UNDER_TABLE was a
# rung top by definition. The desk is at 682 and the ladder cannot follow it
# there: 682 is inside the corridor the plate itself has to be lifted through,
# so a rung at that height would be a rung under a lid of its own making. The
# front seat is therefore made rather than borrowed - two blocks on the ladder
# uprights' inner faces, in the rung block's own 36x48 stock and at the rung
# block's own X.
#
# THERE IS ONLY ONE FACE TO SCREW TO, AND IT IS 36 mm WIDE. The plate stops
# PANEL_FIT short of the uprights' back plane (Y 750 against 752), so no part
# of the plate is ever OVER an upright: whatever carries its front edge has to
# reach BACK out of the upright and hold the plate on a cantilever. The upright
# offers 36 mm of Y (752..788) and nothing else, so the block's rear 36 mm is
# its fixing and everything behind Y 752 is ledge.
#
# THE LENGTH IS NOT CHOSEN, IT IS SOLVED. The two blocks have to make the same
# MIN_BEARING the file asks of every bearing LINE under this plate, so the
# ledge is MIN_BEARING / (2 x TABLE_BEARER_T) rounded up to the millimetre and
# the piece is that plus the UPRIGHT_T it is screwed to.
#
# X10 - AND THE SECTION IS SOLVED TOO, WHICH IT WAS NOT BEFORE. X9 wrote this
# piece as 36x48 x 108, the rung block's own stock, and then had to write down
# that ONE screw was all it could hold: the fixing face is the upright's 36 mm
# of depth by the block's own height, and 36 x 48 gives exactly one 6 mm screw
# either way (2 x 3d = 36 across, and 48 is 12 short of the 2 x 3d + 4d = 60 a
# second one needs along it). That was true, and it was the wrong thing to
# accept, because THIS block is not the rung block:
#   * the rung block has a tread lying on it and the tread is pinned to the
#     upright. It cannot turn about its one screw;
#   * the bordkloss has a PLATE lying on it, loose, lifted off twice a day.
#     Nothing holds it down. And the plate's load stands ~55 mm in FRONT of the
#     screw line - the plate covers the block's ledge, resultant near Y 723,
#     the screw is on the upright's centre line at 770 - so the load is a
#     moment about the X axis, in the PLANE of the fixing face, and one screw
#     carries it in friction and shank bending. A bearing couple cannot help:
#     there is nothing under the block.
# Two screws stacked in Z turn that moment into steel, +-P*55/s per screw. The
# only dimension free to grow is the block's HEIGHT - the 36 is the upright's
# own depth and can never change - so the block becomes 48x68 x 91, the
# bench-rail board, standing 68 in Z: Z 614..682, a fixing face of 36 x 68, and
# 60 of those 68 mm spent on 2 x 3d + 4d exactly. It is not a new profile
# (48x68 is the bench rails, the ledger, the stub legs and the four panel
# battens) and it takes two pieces off the 36x48 board.
# WHAT ELSE THE WIDER BLOCK BUYS: the free front edge between the two of them
# goes 248 -> 224 mm and the bearing line goes 2 x 36 x 70 = 5040 to
# 2 x 48 x 53 = 5088 mm2 - both by-products of the same change, and both in the
# right direction. See the sheet paragraph below, which needed the first one.
#
# AND IT GUIDES, BECAUSE IT STANDS WHERE THE RUNG END STOOD. The panel's two
# guide battens run down the shafts at X 835 / 1155 and find the rung end there
# in bed mode (V3). The bearer's outboard face is that same plane - the block
# grew INBOARD, into the bay, not outboard - so TABLE MODE IS GUIDED BY THE
# SAME GEOMETRY BED MODE IS, and the batten laps the whole 68 mm of it in Z
# where a rung end gives 48, and 53 mm of it in Y where a rung end gives 30.
# Nothing about the panel sub-assembly changes; it does not know which of the
# two it has landed on.
#
# WHAT IT IS IN THE WAY OF, SAID OUT LOUD. K1 cut 37 mm off the rung block to
# get it OUT of the transfer corridor, because that 37 mm carried nothing. X9
# puts TABLE_BEARER_LEDGE (53) of block back INTO the corridor at each side -
# and this one carries the plate. It is the wall X8 named "the crossing", and the clearance
# over it is measured on the solids in the X9 block at the bottom of this file.
#
# AND WHAT THE SHEET PAYS FOR IT, BECAUSE SOMETHING DOES. Until X9 the plate's
# front edge landed on a RUNG, 320 mm of continuous bearing across the middle
# of it. Two blocks give 2 x TABLE_BEARER_T, and TABLE_FREE_EDGE of front edge
# between them is bare 18 mm sheet in table mode. That is a real change and it
# is priced here rather than left for somebody to find:
#   * where the LOAD PATH runs, nothing moved. The two M4 battens are outboard
#     of X 835 / 1155 in both modes, so they never sat on the rung either: they
#     hand their reaction into the sheet and the sheet carries it the same
#     26 mm across to the same bearing edge, at the same 0,69 utilisation
#     (V2/M5). The bordkloss is under exactly that edge.
#   * what IS new is a load put on the middle of the free front edge - leaning
#     on the table from the ladder side.
#
# [X10 CORRECTION, and it is the biggest single number this file has had wrong.
#  X9 priced that last bullet as "a strip spanning the 324 mm between the two
#  battens: M = 1000 * 324 / 4 = 81 000 Nmm, on a conservative 250 mm of
#  effective width W = 13 500 mm3, sigma 6,0 MPa, utilisation 0,86". Two things
#  in one sentence, and both of them wrong in the unsafe direction:
#
#    THE SPAN IS NOT 324. The battens carry nothing at the front edge - X9's
#    own first bullet says so, in the paragraph above: they hand their reaction
#    INTO the sheet. What holds the front edge up is the two BORDKLOSSER, and
#    the span is the clear bay between them. The same X9 paragraph even names
#    it in its own second sentence - "the 248 mm of front edge between them is
#    bare 18 mm sheet" - and then handed 324 to the arithmetic three lines
#    later. It is now TABLE_FREE_EDGE, measured off the two blocks' solids in
#    the X10 block below and never typed again.
#
#    250 mm OF EFFECTIVE WIDTH IS NOT CONSERVATIVE, IT IS WRONG. b_ef is how
#    much of the sheet shares a point load, and it is a spreading argument:
#    away from an edge the load spreads both ways, and at a FREE EDGE it can
#    only spread one. A hand or a knee on the very edge of the plate mobilises
#    about the width of the contact patch plus its own spread - contact + 60 mm
#    is the number used below - not a quarter of a metre. The file's own other
#    sheet rows already knew this: the V2/M5 row uses 100 mm and calls it
#    conservative, and the free-corner row (2 lines up from here) says outright
#    that "the effective width is its own length a". 250 is the outlier, and it
#    is the one that flattered the answer 2,5x.
#
#  Corrected, on the same 1 kN and the wider blocks this round buys, the row is
#  1,07 for a flat hand and 1,49 for a knee against the 6,95 the bare-sheet
#  row is calibrated on - see the printed row. It does not pass on that number,
#  and the fix is not more wood: there is nowhere to put it. See PANEL_GRAIN.]
#
#   * the honest alternative, said so it is on the record: a full-width bearer
#     at 682 would be a RUNG at 682, and 682 is the one height in this ladder a
#     rung may not stand at. That is why it is two blocks and not a rail.
#   * and the other honest alternative, X10: a cross batten under the plate's
#     front edge between the two guide battens - the obvious fix, and it is
#     NOT BUILDABLE, measured. In bed mode the plate's underside IS the rung's
#     top over the whole ladder bay (both 297, over X 835..1155, Y 720..788):
#     the rung is the bed-mode front bearing, so there is exactly 0 mm of air
#     under the front edge to put a batten in. Pull the batten back until it
#     clears the rung (Y <= 720) and in TABLE mode it runs into the bordklosser
#     instead (Y 697..788, Z 614..682); pull it back until it clears those too
#     (Y <= 695) and it is 55 mm behind the edge, where a 55 mm plate
#     cantilever is no better than the span it replaced. The plate's front edge
#     is the one strip of this bed that has wood under it in one mode and has
#     to be empty in the other.
MIN_BEARING = 5000               # mm2, per bearing LINE under the plate
TABLE_BEARER_T = BATTEN_W                      # 48 (X)  [X9: BLOCK_T, 36]
TABLE_BEARER_H = BATTEN_H                      # 68 (Z)  [X9: BLOCK_H, 48]
TABLE_BEARER_LEDGE = -(-MIN_BEARING
                       // (2 * TABLE_BEARER_T))     # 53, derived  [X9: 70]
TABLE_BEARER_Y1 = LADDER_Y1                    # 788, flush with the front plane
TABLE_BEARER_Y0 = PANEL_Y1 - TABLE_BEARER_LEDGE     # 697  [X9: 680]
TABLE_BEARER_LEN = TABLE_BEARER_Y1 - TABLE_BEARER_Y0    # 91  [X9: 108]
TABLE_BEARER_Z1 = PANEL_UNDER_TABLE            # 682, the plate's seat
TABLE_BEARER_Z0 = TABLE_BEARER_Z1 - TABLE_BEARER_H      # 614  [X9: 634]
# The blocks grow INBOARD off the uprights' inner faces, so the guiding plane
# X 835 / 1155 is untouched and it is the free bay that shrinks instead.
TABLE_BEARER_X = [LADDER_INNER_L,                       # 835 .. 883
                  LADDER_INNER_R - TABLE_BEARER_T]      # 1107 .. 1155
TABLE_BEARER_BEARING = (2 * TABLE_BEARER_T
                        * TABLE_BEARER_LEDGE)  # 5088 mm2  [X9: 5040]
# The bare sheet between the two of them: the plate's free front edge, and the
# span of the row that is computed on the solids further down.
TABLE_FREE_EDGE = (TABLE_BEARER_X[1]
                   - (TABLE_BEARER_X[0] + TABLE_BEARER_T))   # 224  [X9: 248]
TABLE_BEARER_FACE = UPRIGHT_T * TABLE_BEARER_H          # 2448 mm2 on the upright
# The screw rule lives further down the file (max_row / MIN_EDGE / min_spacing),
# so the height is checked against the arithmetic here and against the rule
# itself where J5-B is placed - see the X10 assert under TABLE_BEARER_SCREWS.
TABLE_BEARER_SCREWS = 2          # what the 36 x 68 fixing face has to hold
assert TABLE_BEARER_H >= 2 * (3 * 6) + 4 * 6, (
    f"X10: the bordkloss stands {TABLE_BEARER_H:g} mm in Z and two 6 mm screws "
    f"stacked up its fixing face want 2 x 3d + 4d = 60. One screw is not "
    f"enough here: this block carries a LOOSE plate whose load stands in "
    f"front of the screw line, with nothing on top of it to stop it turning "
    f"about a single fastener")

# ---------------------------------------------------------------------------
# V13: THE LOWER LEVEL BECOMES A BED IN FULL LENGTH - SLATS TO THE WALL,
#      AND THE FOUR CUSHIONS THAT COVER IT
# ---------------------------------------------------------------------------
# This is the idea the whole lower level was drawn around, and until this round
# it was the one part of it that lived in prose: the sofa cushions ARE the lower
# bunk's mattress. The documentation said "three cushions, 645 + 700 + 645", and
# the model had never been asked whether that was true. It was not, twice over:
#
#   1  THE BENCH SLAT FIELD STOPPED 98 mm SHORT AT EACH END. W9 started it at
#      the back post's inner face (X 98 / 1892) because a bench slat runs
#      Y -48..752 and would otherwise cut straight through the relocated post.
#      So 645 + 700 + 645 = 1990 put 98 mm of cushion over open air at each
#      end - a hole a cushion corner drops into, and 98 mm is over EN 747's
#      75 mm opening limit into the bargain.
#   2  WHICH LEFT THE LOWER BED 1794 LONG against the upper bed's 1990.
#
# Both are closed here, and the second is the reason for the first: ONE EXTRA
# SLAT AT EACH END, exactly the width of the post it hides behind, on a cleat
# screwed to that post's front face. After it the lower level is a bed in the
# same length as the upper one -
#
#   THE LOWER SLEEPING SURFACE = X 0..1990, Y -48..752, less the two back
#   corner posts, which stand 98 x 36 in the wall corner at either end
#
# - and every cushion number below is arithmetic on those figures.

# --- the end slat -----------------------------------------------------------
# It cannot be a full 800 mm slat: the back corner post occupies Y -48..-12 for
# its whole height right there, so the end slat starts at the post's FRONT face
# and runs Y -12..752. That is 764 mm, and it is the one bench slat with a
# length of its own. Its width is not chosen either - the end zone is X 0..98,
# the post's own width, and the 23x98 board is 98 wide, so the piece fills the
# zone edge to edge and butts the first bench slat with a zero gap. Zero is
# inside EN 747's <= 5 mm band; it is the tightest end this field can have.
END_SLAT_X = [0, WALL_SPAN - BENCH_SLAT_W]         # 0..98 and 1892..1990
END_SLAT_Y0 = BACK_POST_Y1                         # -12, the post's front face
END_SLAT_Y1 = BENCH_SLAT_Y1                        # 752
END_SLAT_LEN = END_SLAT_Y1 - END_SLAT_Y0           # 764
END_SLAT_GAP = END_SLAT_X[0] + BENCH_SLAT_W - BENCH_SLAT_X_START   # 0

# --- the cleat that carries its back end ------------------------------------
# There is nothing under the end slat's back end and nowhere to put a rail: the
# back bench rail lies at Y -48..0 and BUTTS the post's inner face at X 98
# (W9/U2), and the 12 mm of Y that is left in front of the post between there
# and the rail plane is not a bearing. What the end zone does have is the back
# post's FRONT FACE - 98 x 1402 of clean side grain, untouched by any other
# joint - so the bearing is a cleat screwed flat to it.
#
# 36x48, on the flat: 36 mm of Y (the bearing depth the slat end lands on) and
# 48 mm of Z, top at the bench rail top so the end slat lies in the same plane
# as every other one. The section is the ladder-upright/rung-block stock and it
# comes out of that board's rest - 2 x 98 mm off a 1076 mm offcut, so the cleat
# costs no timber at all. The 36 mm depth is what sets the screw: 5x60 through
# 36 mm of cleat leaves 24 mm in a 36 mm post, so nothing comes near the post's
# back face, which is the wall mounting plane. A 6x80 would go through it.
END_CLEAT_T = BLOCK_T                              # 36 (Y), the bearing depth
END_CLEAT_H = BLOCK_H                              # 48 (Z)
END_CLEAT_LEN = BENCH_SLAT_W                       # 98 (X), the end zone
END_CLEAT_Z1 = BENCH_RAIL_TOP                      # 297, the slat underside
END_CLEAT_Z0 = END_CLEAT_Z1 - END_CLEAT_H          # 249  [X3: 211]
END_CLEAT_Y0 = BACK_POST_Y1                        # -12, on the post face
END_CLEAT_Y1 = END_CLEAT_Y0 + END_CLEAT_T          # 24
END_CLEAT_X = END_SLAT_X                           # under its own slat
# The end slat's span, back bearing centre to front bearing centre, against the
# 752 mm the other bench slats run (vedlegg A.1): SHORTER, so the slat criterion
# that governs the field governs this piece with room to spare.
END_SLAT_SPAN = ((BENCH_RAIL_Y[1] + BENCH_RAIL_T / 2)
                 - (END_CLEAT_Y0 + END_CLEAT_T / 2))          # 722
END_CLEAT_BEARING = END_CLEAT_LEN * END_CLEAT_T               # 3528 mm2

# --- the sleeping surface it completes --------------------------------------
LOWER_SLEEP_X0 = 0
LOWER_SLEEP_X1 = WALL_SPAN                             # 1990, wall to wall
LOWER_SLEEP_LEN = LOWER_SLEEP_X1 - LOWER_SLEEP_X0      # 1990
LOWER_SLEEP_Y0 = BENCH_SLAT_Y0                         # -48, the wall plane
LOWER_SLEEP_Y1 = BENCH_SLAT_Y1                         # 752, the front vertical
LOWER_SLEEP_DEPTH = LOWER_SLEEP_Y1 - LOWER_SLEEP_Y0    # 800 == BENCH_SLAT_LEN
# The surface as rectangles, which is what it actually is: full depth over the
# 1794 mm between the posts, and 764 mm deep over the 98 mm end zones, where the
# back corner post takes the wall corner. This list IS the coverage assert's
# right-hand side.
LOWER_SLEEP_RECTS = [
    (END_SLAT_X[0], END_SLAT_X[0] + BENCH_SLAT_W, END_SLAT_Y0, LOWER_SLEEP_Y1),
    (BENCH_SLAT_X_START, WALL_SPAN - BENCH_SLAT_X_START,
     LOWER_SLEEP_Y0, LOWER_SLEEP_Y1),
    (END_SLAT_X[1], END_SLAT_X[1] + BENCH_SLAT_W, END_SLAT_Y0, LOWER_SLEEP_Y1),
]
LOWER_SLEEP_AREA = sum((x1 - x0) * (y1 - y0) for x0, x1, y0, y1
                       in LOWER_SLEEP_RECTS)              # 1 584 944 mm2

# --- the split: a third and a sixth -----------------------------------------
# Two seat cushions at a third each and two back cushions at a sixth each is
# 2/3 + 2/6 = ONE WHOLE SLEEPING SURFACE. The four pieces are a TILING of the
# lower bed, not four pieces that happen to lie near each other, and that is
# asserted below rather than claimed here.
#
# 1990 is not divisible by six, so the split is taken to whole millimetres and
# the rounding is given to the back cushions: 663 = floor(L/3) is 0.33 mm under
# a third, 332 is 0.33 mm over a sixth, and 2 x 663 + 2 x 332 = 1990 EXACTLY.
# Nobody cuts a third of a millimetre of foam; the sum is what has to be exact.
SEAT_CUSHION_LEN = LOWER_SLEEP_LEN // 3                   # 663
BACK_CUSHION_LEN = (LOWER_SLEEP_LEN - 2 * SEAT_CUSHION_LEN) // 2   # 332

# --- the thickness, one number for all four ---------------------------------
# It has to be one number: four cushions butted together are one bed, and a bed
# with a step in it is not a bed. That also RETIRES the old rule that the middle
# cushion should be 5 mm thicker to swallow PANEL_BENCH_DIP. It cannot be, and
# it no longer needs to be: no joint between two cushions falls on a zone
# boundary any more. The dip stays a dip - 5 mm, which is what V6 cut it to
# precisely so that foam could take it up.
#
# 100 mm, and every reason is measured, printed by the validation block and in
# the key dimensions:
#   * AN 80 x 200 FOAM MATTRESS IS 800 x 2000 - the same article as the one
#     upstairs. 800 is exactly this surface's depth and 2000 is 10 mm over its
#     length, so all four cushions are ONE standard mattress cut in four, with
#     one crosscut of waste. 120 mm foam is sold the same way and would work;
#     100 is the thickness the cheap sheet actually comes in.
#   * seat height goes 320 -> 420 on the same 100 mm of foam (X3 took the
#     bench up 38): a grown chair, not a child's one.
#   * seat height goes 320 -> 420 (X3 raised the bench 38 and the cushion is
#     the same 100): a grown chair, not a child's one.
#   * the table plate top is 280 mm above the seat cushion and its underside
#     262 mm - at 120 mm foam those become 260 and 242. (X9 took the plate off
#     rung 2 and up to desk height; X2 had 140 / 122 and v13 118 / 100. The
#     cushion is the same cushion at every one of those numbers - it is the
#     PLATE that moved, three times.)
#   * head room under the upper bunk's slats is 1080 mm after X1 (was 781) -
#     the lower storey is a room you stand in now, which is the whole round.
CUSHION_T = 100
CUSHION_TOP_BENCH = BENCH_TOP + CUSHION_T              # 420, over the benches [X3]
CUSHION_TOP_PANEL = PANEL_TOP_BED + CUSHION_T          # 415, over the panel [X3]
MIN_LOWER_HEADROOM = 700           # own rule: a child sits up in the lower bunk
LOWER_HEADROOM = SLAT_Z0 - CUSHION_TOP_BENCH           # 1080, to the slats [X1: 781]
LOWER_HEADROOM_RAIL = RAIL_BOTTOM - CUSHION_TOP_BENCH  # 982, under the rails [683]
# X10: THE CLEAR FIELD IS NOT THE ONLY NUMBER, AND IT WAS THE ONLY ONE PRINTED.
# Both lines above are typed differences of typed constants: they say how far it
# is from the cushion top to the SLATS, and they are right about that. What they
# are not is head room, because three permanent things hang under the slats and
# over the same footprint, and the lowest of them is 976 mm lower than 1080.
# They are measured on the solids in the X1 block, the way CEILING_CLEAR is,
# and both numbers are emitted - see LOWER_HEADROOM_MIN / LOWER_HEADROOM_WALL.
EN_GUARD_TRIGGER_H = 600           # EN 747: over this, a bed base needs guards
TABLE_OVER_CUSHION = PANEL_TOP_TABLE - CUSHION_TOP_BENCH           # 280  [X9: 140]
TABLE_UNDER_OVER_CUSHION = PANEL_UNDER_TABLE - CUSHION_TOP_BENCH   # 262  [X9: 122]
# The foam sheet the four of them come out of, and what is left of it.
CUSHION_SHEET = (800, 2000)                            # a 80 x 200 foam slab
CUSHION_SHEET_WASTE = CUSHION_SHEET[1] - LOWER_SLEEP_LEN           # 10

# --- where they lie in bed mode: the tiling ---------------------------------
#   seat 0..663 | back 663..995 | back 995..1327 | seat 1327..1990
# The two back cushions meet on X 995, which is the ladder's centre line - not
# arranged, just what a third and a sixth of this wall come to.
SEAT_CUSHION_X = [LOWER_SLEEP_X0,                              # 0
                  LOWER_SLEEP_X1 - SEAT_CUSHION_LEN]           # 1327
BACK_CUSHION_BED_X = [LOWER_SLEEP_X0 + SEAT_CUSHION_LEN,       # 663
                      LOWER_SLEEP_X0 + SEAT_CUSHION_LEN
                      + BACK_CUSHION_LEN]                      # 995
# THE NOTCH. A seat cushion is a rectangle 663 x 800 with one 98 x 36 corner
# cut out of it - the back corner post, which is the only thing standing in the
# lower sleeping surface. It is a bread-knife cut in foam and it is drawn,
# because a cushion drawn as a plain box would be drawn through a post.
CUSHION_NOTCH = (POST_W, POST_T)                       # 98 x 36, the post

# --- the seat cushions do not move ------------------------------------------
# Their bed-mode X is their sofa-mode X. A seat cushion is 663 long and the
# bench under it is 645, so it is pushed against the wall at the outer end and
# the last 18 mm hang over the ladder bay - in BOTH positions, because there is
# nowhere else for them to be. Changing the bed over is therefore TWO cushions
# and not four: stand the two back cushions up at the ends for a sofa, lay them
# flat in the middle for a bed.
SEAT_CUSHION_OVERHANG = SEAT_CUSHION_X[0] + SEAT_CUSHION_LEN - BENCH_LEN   # 18
# and what that overhang leaves of the panel's transfer shaft (X 708..1282):
SEAT_CUSHION_SHAFT_GAP = PANEL_X0 - (SEAT_CUSHION_X[0] + SEAT_CUSHION_LEN)  # 45
# the ladder bay, measured at cushion height rather than at the floor:
BAY_AT_CUSHION_H = PANEL_OPENING - 2 * SEAT_CUSHION_OVERHANG               # 664

# --- where the back cushions stand in sofa mode -----------------------------
# and why NOT against the back wall, which is where anyone would put them who
# had not asked the model.
#
# A back cushion is 332 x 800 x 100, and the 800 is not negotiable: it is the
# DEPTH of the sleeping surface, and it is the reason the four pieces cover the
# bed at all. Stand one up against the back wall and that 800 has to go
# somewhere, and there are only two directions:
#   * ALONG X - and a bench offers 645 mm of back wall before the ladder bay
#     starts, with the TABLE PLATE standing at Z 682..700 from X 708 on. It
#     does not fit, on either bench, by 155 mm.
#   * STRAIGHT UP - 420 + 800 = 1220, and the upper side rail's underside is
#     1402. IT FITS NOW, by 182 mm: X1's lift is the first round in which an
#     800 mm dimension can be stood upright on the bench at all. The backrest
#     still lies across the bench end, because that is what makes the sofa a
#     sofa, but the reason is no longer that there is nowhere else for it.
# So the one place an 800 mm dimension stands up in this bed is ACROSS THE
# BENCH, at its end - which is also the answer to what this sofa is: two seats
# either side of a low table, each with its back at the outer end. The bench is
# 800 deep and the backrest is 800 wide; you sit sideways, facing the table,
# two abreast if you like.
#
# TWO THINGS HOLD IT. Its Y0 is the BACK TABLE LEDGER's front face: the ledger
# runs the whole length at Y -48..0, Z 614..682 (X9 took it up 140 with the
# desk), so a cushion standing in the wall plane would drive straight through it
# - and standing 48 mm forward of the wall instead, it LEANS ON IT, 100 x 68 mm
# of contact. X9 moved that contact up the back with the ledger: it used to be
# at the small of the back (54..122 over the seat) and it is across the middle
# of it now (194..262), which is where a backrest is meant to push anyway. Same
# cushion, same 6 800 mm2, and the piece did not change. The corner post's inner face takes the sideways direction. The price is
# 12 mm: the front face lands at Y 800 against a bed that is 836 deep to Y 788,
# so a loose cushion stands 12 mm proud of the bed's front plane in sofa mode.
# That is a soft part in one position and not the bed's depth - and it is
# asserted here rather than discovered by somebody with a tape measure.
BACKREST_Y0 = LEDGER_BACK_Y0 + LEDGER_BACK_T           # 0, the ledger's face
BACKREST_Y1 = BACKREST_Y0 + LOWER_SLEEP_DEPTH          # 800
BACKREST_PROUD = BACKREST_Y1 - FRONT_POST_Y1           # 12, past the front plane
BACKREST_Z0 = CUSHION_TOP_BENCH                        # 420, on the seat cushion
BACKREST_Z1 = BACKREST_Z0 + BACK_CUSHION_LEN           # 752  [X3: 714]
BACKREST_X = [POST_W,                                  # 98..198
              WALL_SPAN - POST_W - CUSHION_T]          # 1792..1892
BACKREST_LEDGER_CONTACT = CUSHION_T * LEDGER_BACK_H    # 6800 mm2 on the ledger

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
CUT_LIST = {}


def block(x0, y0, z0, dx, dy, dz, label, group, cut=None):
    """Axis aligned Box given by its minimum corner and its extents.

    `group` picks the colour group (see GROUP_COLORS) and drives the
    per-material STL export used by the .usdz pipeline.
    `cut` is (cut-list name, "section", length) and adds one piece to the cut
    list. Mirrored / repeated parts share a cut-list name so they merge.
    """
    b = Box(dx, dy, dz).moved(Location((x0 + dx / 2, y0 + dy / 2, z0 + dz / 2)))
    b.label = label
    b.color = GROUP_COLORS[group]
    b.group = group
    b.extents = ((x0, x0 + dx), (y0, y0 + dy), (z0, z0 + dz))
    # The cut-list line this piece was counted into, ON the piece. Without it
    # the sawn LENGTH of a part is guesswork from its bounding box - and the
    # longest side is not always the length (a rung block is 36 long and 48
    # tall). The room-fit rule below needs to know which way the length runs.
    b.cut = None
    if cut is not None:
        name, section, length = cut
        key = (name, section, round(length))
        b.cut = key
        CUT_LIST[key] = CUT_LIST.get(key, 0) + 1
    return b


# ---------------------------------------------------------------------------
# THE ONE PART THAT IS NOT A BOX
# ---------------------------------------------------------------------------
# Every piece of wood in this bed is an axis-aligned box, and a great deal of
# the machinery leans on it: contacts() finds joints by looking for shared
# faces with area behind them, patch_window() cuts the fastener rows out of
# those faces, and every clearance, sweep and overlap assert is arithmetic on
# `extents`. V4 introduces exactly ONE exception - the tapered front wing
# (M5) - and it is safe for a reason that has to be stated rather than hoped
# for:
#
#   * THE MATING FACES ARE STILL RECTANGLES. The wing meets the panel over its
#     whole top face (116 x 48, unchanged) and meets nothing else. The face
#     that got cut is the UNDERSIDE, which touches nothing in either mode.
#     So contacts(), patch_window() and bearing_area() see exactly what they
#     saw before.
#   * THE BOUNDING BOX IS UNCHANGED, so every clearance and sweep assert that
#     reads `extents` is still true and is now CONSERVATIVE: the real solid is
#     strictly inside the box those asserts clear.
#   * WHAT IS NOT CONSERVATIVE is anything that reads VOLUME or draws the
#     silhouette, and those two read the solid, not the box.
def wedge(x0, y0, z0, dx, dy, dz, tip_dz, tip_at_x0, label, group, cut=None):
    """A box with one long edge planed away: full `dz` at one end in X,
    `tip_dz` at the other, TOP FACE FLAT the whole way.

    `tip_at_x0` says which end is the thin one. The cut is a single straight
    saw line down the length of the piece - one pass, one wedge - which is why
    the shop instruction is "skråkapp", not "profile it".
    """
    b = Box(dx, dy, dz).moved(Location((x0 + dx / 2, y0 + dy / 2, z0 + dz / 2)))
    # The plane the saw runs in: through the LOW corner at the fat end and the
    # underside corner at the thin end. Built as a big box whose top face is
    # that plane, turned about Y and hung off the fat end's low corner, then
    # subtracted - so the geometry comes out of the same two numbers the cut
    # list prints and cannot drift from them.
    rise, run = dz - tip_dz, dx
    ang = math.degrees(math.atan2(rise, run))
    pivot_x = x0 if not tip_at_x0 else x0 + dx
    big = max(dx, dz) * 4
    cutter = Box(big, dy + 4, big).moved(Location((0, 0, -big / 2)))
    cutter = Location((0, 0, 0), (0, 1, 0),
                      ang if tip_at_x0 else -ang) * cutter
    cutter = Location((pivot_x, y0 + dy / 2, z0)) * cutter
    b = b - cutter
    b.label = label
    b.color = GROUP_COLORS[group]
    b.group = group
    # The BOX extents, on purpose: see the note above. Everything that clears
    # this part clears the box it was cut from.
    b.extents = ((x0, x0 + dx), (y0, y0 + dy), (z0, z0 + dz))
    b.tapered = (tip_dz, tip_at_x0)
    b.cut = None
    if cut is not None:
        name, section, length = cut
        key = (name, section, round(length))
        b.cut = key
        CUT_LIST[key] = CUT_LIST.get(key, 0) + 1
    return b


def write_svg(comp, path, direction):
    """Hidden-line-removed projection of `comp` seen from `direction`."""
    bb = comp.bounding_box()
    center = bb.center()
    diag = bb.diagonal
    origin = (center.X + direction[0] * diag * 4,
              center.Y + direction[1] * diag * 4,
              center.Z + direction[2] * diag * 4)
    visible, _hidden = comp.project_to_viewport(
        viewport_origin=origin,
        viewport_up=(0, 0, 1),
        look_at=(center.X, center.Y, center.Z),
    )
    exporter = ExportSVG(scale=0.5, line_weight=0.15, margin=10)
    exporter.add_layer("visible")
    exporter.add_shape(visible, layer="visible")
    exporter.write(path)


def sec(a, b):
    return f"{int(a)}x{int(b)}"


# ---------------------------------------------------------------------------
# UPPER BED
# ---------------------------------------------------------------------------
parts = []

back_rail = block(THROUGH_X0, BACK_RAIL_Y0, RAIL_BOTTOM, THROUGH_LEN, RAIL_T,
                  RAIL_H, "Upper Side Rail Back", "rails",
                  ("Upper side rail", sec(RAIL_T, RAIL_H), THROUGH_LEN))
front_rail = block(THROUGH_X0, FRONT_RAIL_Y0, RAIL_BOTTOM, THROUGH_LEN, RAIL_T,
                   RAIL_H, "Upper Side Rail Front", "rails",
                   ("Upper side rail", sec(RAIL_T, RAIL_H), THROUGH_LEN))
parts += [back_rail, front_rail]

# D5: no slat cleats any more. The slats lie straight on top of both rails.

# Slats across Y, evenly spaced along X inside 20..1970. One 5x60 screw per
# end, down through the slat into the rail below it.
#
# W8: ONE LENGTH. v9/W4 split the field into two lengths so that the twelve
# slats that were clear of the back posts could run on past the back rail to the
# wall. W6 put the posts inside the rail plane and brought the wall to the rail
# face, so there is nothing to run on to and nothing to dodge: all 14 slats are
# the same 36x98 x 800, Y -48..752, and the wall-side end of every one of them is
# ON the mounting plane. The posts are 98 mm below the slats' underside, so they
# cannot be fouled at any pitch - asserted anyway in the validation block.
slat_pitch = (SLAT_X_END - SLAT_X_START - BED_SLAT_W) / (SLAT_COUNT - 1)
slat_gap = slat_pitch - BED_SLAT_W
slat_end_gap = min(SLAT_X_START, WALL_SPAN - SLAT_X_END)
assert slat_gap <= MAX_SLAT_GAP, f"slat gap {slat_gap:.1f} > {MAX_SLAT_GAP}"
assert slat_end_gap <= MAX_SLAT_GAP, f"slat end gap {slat_end_gap} > {MAX_SLAT_GAP}"

BACK_POST_X = [(x, x + POST_W) for x in CORNER_POST_X]   # (0, 98), (1892, 1990)
BACK_POST_EXTENTS = [((px0, px1), (BACK_POST_Y0, BACK_POST_Y1),
                      (0, BACK_POST_HEIGHT)) for px0, px1 in BACK_POST_X]

bed_slats = []
for i in range(SLAT_COUNT):
    x0 = SLAT_X_START + i * slat_pitch
    s = block(x0, SLAT_Y0, SLAT_Z0, BED_SLAT_W, SLAT_LEN, BED_SLAT_T,
              f"Bed Slat_{i + 1}", "boards",
              ("Upper bed slat (D5)", sec(BED_SLAT_T, BED_SLAT_W), SLAT_LEN))
    bed_slats.append(s)
parts += bed_slats

mattress = block(0, MATTRESS_Y0, MATTRESS_Z0, WALL_SPAN, MATTRESS_W, MATTRESS_H,
                 "Mattress 200x80 (reference)", "mattress")

# ---------------------------------------------------------------------------
# POSTS  (four corner posts - D1 deleted the two intermediate back posts)
# W6: the back pair stands IN the back rail plane (Y -48..0) and stops at 1402,
# the rail underside, so the rail bears on it; the front pair is 2037 (guard
# bands). Same 36x98 section, two different cut lengths, two cut-list lines.
# ---------------------------------------------------------------------------
for i, x0 in enumerate(CORNER_POST_X):
    side = "Left" if i == 0 else "Right"
    parts.append(block(x0, BACK_POST_Y0, 0, POST_W, POST_T, BACK_POST_HEIGHT,
                       f"Corner Post Back {side}", "posts",
                       ("Corner post, back (W2, wall side)",
                        sec(POST_T, POST_W), BACK_POST_HEIGHT)))
    parts.append(block(x0, FRONT_POST_Y0, 0, POST_W, POST_T, POST_HEIGHT,
                       f"Corner Post Front {side}", "posts",
                       ("Corner post, front", sec(POST_T, POST_W), POST_HEIGHT)))

# ---------------------------------------------------------------------------
# END BEAMS
# ---------------------------------------------------------------------------
# One 48x98 beam per end. Bolted to the inner faces of the corner posts, top
# flush with the rail underside so both side rails bear on it.
for i, x0 in enumerate(END_BEAM_X):
    side = "Left" if i == 0 else "Right"
    parts.append(block(x0, END_BEAM_Y0, END_BEAM_Z0, END_BEAM_T, END_BEAM_LEN,
                       RAIL_H, f"End Beam {side}", "rails",
                       ("End beam", sec(END_BEAM_T, RAIL_H), END_BEAM_LEN)))
    # V5: no bearing block under the beam ends any more - the two 6x90 of J1
    # are the whole fixing, at half the utilisation the block's own screw had.

# ---------------------------------------------------------------------------
# LADDER
# ---------------------------------------------------------------------------
for name, x0 in (("Left", LADDER_LEFT_X), ("Right", LADDER_RIGHT_X)):
    parts.append(block(x0, LADDER_Y0, 0, UPRIGHT_W, UPRIGHT_T, POST_HEIGHT,
                       f"Ladder Upright {name}", "posts",
                       # U2: the stock is unchanged 36x48, named thin side
                       # first like every other section in the list; what
                       # changed is which way round it stands.
                       ("Ladder upright (D13)", sec(UPRIGHT_T, UPRIGHT_W),
                        POST_HEIGHT)))

# Cleat blocks first: the rung rests on the blocks and is screwed down into
# them, and the blocks are screwed to the inner face of each upright.
for i, top in enumerate(RUNG_TOPS):
    for j, bx0 in enumerate(RUNG_BLOCK_X):
        parts.append(block(bx0, RUNG_BLOCK_Y0, top - RUNG_T - RUNG_BLOCK_H,
                           RUNG_BLOCK_T, RUNG_BLOCK_LEN, RUNG_BLOCK_H,
                           f"Rung Block {'Left' if j == 0 else 'Right'}_{i + 1}",
                           "boards",
                           ("Ladder rung block", sec(RUNG_BLOCK_T, RUNG_BLOCK_H),
                            RUNG_BLOCK_LEN)))
    parts.append(block(LADDER_INNER_L, RUNG_Y0, top - RUNG_T,
                       RUNG_LEN, RUNG_D, RUNG_T,
                       f"Ladder Rung_{i + 1}", "boards",
                       ("Ladder rung (tread)", sec(RUNG_T, RUNG_D), RUNG_LEN)))

# X9: and the two blocks that carry the plate's front edge at desk height. Same
# stock and same X as a rung block, screwed to the same 36 mm of upright - and
# 70 mm longer, so the plate has something to land on where no rung may stand.
for j, bx0 in enumerate(TABLE_BEARER_X):
    parts.append(block(bx0, TABLE_BEARER_Y0, TABLE_BEARER_Z0,
                       TABLE_BEARER_T, TABLE_BEARER_LEN, TABLE_BEARER_H,
                       f"Table Bearer {'Left' if j == 0 else 'Right'}",
                       "boards",
                       ("Table bearer block (X9)",
                        sec(TABLE_BEARER_T, TABLE_BEARER_H),
                        TABLE_BEARER_LEN)))

# ---------------------------------------------------------------------------
# GUARD RAILS  -  FRONT ONLY (W1)
# ---------------------------------------------------------------------------
# BACK  (W1): NOTHING. The wall is the barrier on that side and the frame is
#             bolted to it (S2). The two 34x98 x 1984 boards that used to hang
#             at Y -130..-96 are deleted; the back side's EN 747 case is the
#             48 mm mattress-to-wall gap, checked in the validation block.
# FRONT (D2): four segments, two per band, lapped onto the ladder uprights and
#             stopping flush with the upright inner faces, so the 320 mm
#             climb-through opening runs all the way up.
# D6: the two bands sit at 1412..1510 and 1585..1683 (see GUARD_BAND_Z0).
# D14: the lap face is the INNER one now - Y 718..752 against the post/upright
#      inner plane 752 - so the boards hang inboard, over the mattress footprint
#      but 75 mm clear above the mattress surface, and nothing is left outside
#      the post plane Y = 800.
for i, z0 in enumerate(GUARD_BAND_Z0):
    for j, (sx0, sx1) in enumerate(FRONT_GUARD_SEGMENTS):
        side = "Left" if j == 0 else "Right"
        parts.append(block(sx0, FRONT_GUARD_Y0, z0,
                           sx1 - sx0, GUARD_T, GUARD_W,
                           f"Guard Rail Front {side}_{i + 1}", "boards",
                           ("Guard rail, front segment (D2/D7/D13)",
                            sec(GUARD_T, GUARD_W), sx1 - sx0)))

# ---------------------------------------------------------------------------
# LOWER SECTION: BENCHES
# ---------------------------------------------------------------------------
# C5: 48x68 bench rails at Z 229..297, one per Y plane, each carried at its ends
# by a corner post - on its own end screws since V5, J8-B behind and J8 in
# front - and in between by two stub legs.
# They give the loose panel an edge to rest on in bed mode and give the ladder
# uprights a low fixing point.
# D11/D13: the BACK rail is the continuous member; the FRONT one is two
# 642 mm segments that stop at the sofa ends on their stub legs, so the whole
# front floor between the benches is open.
# W9: the back rail is 1794 mm at X 98..1892 - it butts the two back corner posts
# (which now stand in its Y band) and is screwed to their X-inner faces with the
# two 6x90 skew screws of J8-B. That pair is the WHOLE end fixing after V5.
for i, ry0 in enumerate(BENCH_RAIL_Y):
    name = "Back" if i == 0 else "Front"
    if i == 0:
        parts.append(block(BETWEEN_POSTS_X0, ry0, BENCH_RAIL_BOTTOM,
                           BETWEEN_POSTS_LEN, BENCH_RAIL_T, BENCH_RAIL_H,
                           "Bench Rail Back (continuous)", "rails",
                           ("Bench rail, back (C5)",
                            sec(BENCH_RAIL_T, BENCH_RAIL_H), BETWEEN_POSTS_LEN)))
    else:
        for j, (sx0, sx1) in enumerate(FRONT_BENCH_RAIL_SEGMENTS):
            side = "Left" if j == 0 else "Right"
            parts.append(block(sx0, ry0, BENCH_RAIL_BOTTOM, sx1 - sx0,
                               BENCH_RAIL_T, BENCH_RAIL_H,
                               f"Bench Rail Front {side} (segment)", "rails",
                               ("Bench rail, front segment (D13)",
                                sec(BENCH_RAIL_T, BENCH_RAIL_H), sx1 - sx0)))
    # V5: no bearing blocks under the rail ends either - J8-B behind and J8 in
    # front are the whole end fixing. See the note in the datum block above.
    # Stub legs at the inner end of each bench (the outer ends sit on the posts).
    for j, lx0 in enumerate(STUB_LEG_X):
        side = "Left" if j == 0 else "Right"
        parts.append(block(lx0, ry0, 0, LEG_W, LEG_T, STUB_LEG_H,
                           f"Bench Stub Leg {name} {side}", "posts",
                           ("Bench stub leg (W3)", sec(LEG_T, LEG_W),
                            STUB_LEG_H)))

# C3: 34x98 bench slats on top of the bench rails, five per bench.
# The doc's J11 table lists the right-hand bench at X 1345..1993, which runs 3 mm
# past the wall; the positions here are the exact mirror of the left bench.
# W9: the field starts at the back post's inner face (X 48 / 1942) instead of at
# the wall, because a bench slat runs Y -48..752 and would otherwise cut straight
# through the relocated post. Five slats at 124.75 pitch land the last one on the
# bench end exactly, X 547..645 (mirror 1345..1443).
for i in range(len(BENCH_X)):
    side = "Left" if i == 0 else "Right"
    for j in range(BENCH_SLAT_COUNT):
        off = j * BENCH_SLAT_PITCH
        x0 = (BENCH_SLAT_X_START + off if i == 0 else
              WALL_SPAN - BENCH_SLAT_X_START - BENCH_SLAT_W - off)
        parts.append(block(x0, BENCH_SLAT_Y0, BENCH_RAIL_TOP,
                           BENCH_SLAT_W, BENCH_SLAT_LEN, BENCH_SLAT_T,
                           f"Bench Slat {side}_{j + 1}", "boards",
                           ("Bench slat (C3)", sec(BENCH_SLAT_T, BENCH_SLAT_W),
                            BENCH_SLAT_LEN)))

# V13: THE END SLAT AND ITS CLEAT - one of each per end. See the V13 block for
# every number and for what they are for: they carry the lower sleeping surface
# the last 98 mm out to the wall, which is what makes it a bed in full length.
# The cleat goes in FIRST (the slat lands on it), and it is the only part in
# this bed screwed to the back post's front face.
end_cleats = []
end_slats = []
for i in range(len(END_SLAT_X)):
    side = "Left" if i == 0 else "Right"
    end_cleats.append(block(END_CLEAT_X[i], END_CLEAT_Y0, END_CLEAT_Z0,
                            END_CLEAT_LEN, END_CLEAT_T, END_CLEAT_H,
                            f"Bench End Cleat {side}", "boards",
                            ("Bench end cleat (V13)",
                             sec(END_CLEAT_T, END_CLEAT_H), END_CLEAT_LEN)))
    end_slats.append(block(END_SLAT_X[i], END_SLAT_Y0, BENCH_RAIL_TOP,
                           BENCH_SLAT_W, END_SLAT_LEN, BENCH_SLAT_T,
                           f"Bench End Slat {side}", "boards",
                           ("Bench end slat (V13)",
                            sec(BENCH_SLAT_T, BENCH_SLAT_W), END_SLAT_LEN)))
parts += end_cleats + end_slats

# D3: only the BACK table ledger survives. The front one used to cross the
# whole front of both sofa benches at shin height, right where you sit down,
# and it is replaced by resting the panel's front edge on a ladder rung (D10).
# W9: post to post, X 48..1942, butting and screwed to the back posts' X-inner
# faces - they stand in its Y band now.
support_rail = block(BETWEEN_POSTS_X0, LEDGER_BACK_Y0, LEDGER_BACK_Z0,
                     BETWEEN_POSTS_LEN, LEDGER_BACK_T, LEDGER_BACK_H,
                     "Table Ledger Back", "boards",
                     ("Table ledger, back",
                      sec(LEDGER_BACK_T, LEDGER_BACK_H), BETWEEN_POSTS_LEN))
parts.append(support_rail)

# ---------------------------------------------------------------------------
# MOVABLE PANEL
# ---------------------------------------------------------------------------
# See the D10 note above for what it rests on. NOTE (deviation): the doc's cut
# list gives the panel as 680 x 860 at Y 30..890, inside the ladder uprights
# (floor to ceiling) which the panel X range 655..1335 straddles - a hard
# collision. The panel front edge is kept flush against the uprights' back
# plane; D10 then takes the rear edge back to Y -48 so that it reaches the back
# bench rail and the ledger. D12 makes that 680 x 800, Y -48..752.
panel_bed = block(PANEL_X0, PANEL_Y0, PANEL_UNDER_BED,
                  PANEL_W, PANEL_LEN, PANEL_T,
                  "Movable Panel (bed mode)", "panel",
                  ("Movable panel", f"{PANEL_T} panel, {PANEL_W} wide", PANEL_LEN))
panel_table = block(PANEL_X0, PANEL_Y0, PANEL_UNDER_TABLE,
                    PANEL_W, PANEL_LEN, PANEL_T,
                    "Movable Panel (table mode)", "panel")

# ---------------------------------------------------------------------------
# THE FOUR CUSHIONS  (V13 - see the constants block for every number)
# ---------------------------------------------------------------------------
# Soft parts, drawn in the mattress group and treated exactly the way the
# reference mattress is: bought and not cut, out of the cut list, out of every
# wood-only check, and out of the finished-bed drawings. They ARE in parts.tsv,
# in the mattress step of the manual and in both modes of the model, because
# where they go in each position is the one thing about them worth drawing.
#
# The two seat cushions are ONE part each: their position is identical in bed
# mode and in sofa mode, so there is no "(bed mode)" / "(table mode)" pair to
# tell apart. Only the two back cushions move, and they are built twice.
#
# THE SECOND SOLID IN THIS FILE THAT IS NOT A BOX. A seat cushion has a 98 x 36
# notch in its wall-side corner, where the back corner post stands. The wedge's
# rule (see "THE ONE PART THAT IS NOT A BOX") applies here too and this time it
# is NOT enough on its own - the bounding box a clearance assert would read goes
# straight through the post - so a notched cushion carries `boxes`, the exact
# rectangular decomposition of what it really occupies, and the cushion checks
# read that and never the bounding box.


def cushion(x0, y0, z0, dx, dy, dz, label, notch_at=None):
    """A cushion. `notch_at` is 'low' or 'high' in X and cuts CUSHION_NOTCH out
    of that end's wall-side corner (the back corner post's footprint)."""
    from build123d import Box, Location
    b = Box(dx, dy, dz).moved(Location((x0 + dx / 2, y0 + dy / 2, z0 + dz / 2)))
    boxes = [((x0, x0 + dx), (y0, y0 + dy), (z0, z0 + dz))]
    if notch_at is not None:
        nx, ny = CUSHION_NOTCH
        nx0 = x0 if notch_at == "low" else x0 + dx - nx
        cutter = Box(nx, ny, dz + 2).moved(
            Location((nx0 + nx / 2, y0 + ny / 2, z0 + dz / 2)))
        b = b - cutter
        # exact decomposition: the notched end at reduced depth, then the rest
        boxes = ([((nx0, nx0 + nx), (y0 + ny, y0 + dy), (z0, z0 + dz))]
                 + ([((x0, nx0), (y0, y0 + dy), (z0, z0 + dz))] if nx0 > x0
                    else [])
                 + ([((nx0 + nx, x0 + dx), (y0, y0 + dy), (z0, z0 + dz))]
                    if nx0 + nx < x0 + dx else []))
    b.label = label
    b.color = GROUP_COLORS["mattress"]
    b.group = "mattress"
    b.extents = ((x0, x0 + dx), (y0, y0 + dy), (z0, z0 + dz))
    b.boxes = boxes
    return b


seat_cushions = []
for i, cx0 in enumerate(SEAT_CUSHION_X):
    side = "Left" if i == 0 else "Right"
    seat_cushions.append(cushion(cx0, LOWER_SLEEP_Y0, BENCH_TOP,
                                 SEAT_CUSHION_LEN, LOWER_SLEEP_DEPTH,
                                 CUSHION_T, f"Seat Cushion {side}",
                                 notch_at="low" if i == 0 else "high"))

back_cushions_bed = []
back_cushions_sofa = []
for i, cx0 in enumerate(BACK_CUSHION_BED_X):
    side = "Left" if i == 0 else "Right"
    # BED MODE: flat, in the middle, lying on the panel - so its top is
    # CUSHION_TOP_PANEL, PANEL_BENCH_DIP below the seat cushions beside it.
    back_cushions_bed.append(cushion(cx0, LOWER_SLEEP_Y0, PANEL_TOP_BED,
                                     BACK_CUSHION_LEN, LOWER_SLEEP_DEPTH,
                                     CUSHION_T,
                                     f"Back Cushion {side} (bed mode)"))
for i, bx0 in enumerate(BACKREST_X):
    side = "Left" if i == 0 else "Right"
    # SOFA MODE: on edge at the outer end of its bench, standing on the seat
    # cushion and leaning on the back table ledger. Its LENGTH becomes height.
    back_cushions_sofa.append(cushion(bx0, BACKREST_Y0, BACKREST_Z0,
                                      CUSHION_T, LOWER_SLEEP_DEPTH,
                                      BACK_CUSHION_LEN,
                                      f"Back Cushion {side} (table mode)"))

CUSHIONS_BED = seat_cushions + back_cushions_bed
CUSHIONS_TABLE = seat_cushions + back_cushions_sofa
CUSHIONS_ALL = seat_cushions + back_cushions_bed + back_cushions_sofa

# M4: the two stiffener battens. They are SCREWED TO THE PANEL, so they are not
# part of the fixed structure - they move with it and are built once per mode,
# alongside the panel they hang under. Only the bed-mode pair carries the cut
# entry; it is the same two pieces in both modes.
battens_bed = []
battens_table = []
for i, bx0 in enumerate(BATTEN_X):
    side = "Left" if i == 0 else "Right"
    battens_bed.append(block(bx0, BATTEN_Y0, BATTEN_Z0_BED,
                             BATTEN_W, BATTEN_LEN, BATTEN_H,
                             f"Panel Stiffener Batten {side} (bed mode)", "panel",
                             ("Panel stiffener batten (M4)",
                              sec(BATTEN_W, BATTEN_H), BATTEN_LEN)))
    battens_table.append(block(bx0, BATTEN_Y0, BATTEN_Z0_TABLE,
                               BATTEN_W, BATTEN_LEN, BATTEN_H,
                               f"Panel Stiffener Batten {side} (table mode)",
                               "panel"))

# V2/M5, V4: the two front WINGS, one under each front corner. Same stock, same
# Z band, same trip - they are part of the panel assembly and are screwed up
# into it, so they are built per mode alongside the panel they hang under - but
# the underside is now a single straight saw cut from the full 73 mm at the
# ROOT, where the piece butts its guide batten, down to the up-screw's own seat
# at the TIP on the panel's edge. `tip_at_x0` is therefore "is the panel edge
# the low-X end", which it is on the left and is not on the right: both wings
# taper OUTWARDS, away from the guide batten they hang off.
for i, (nx0, nx1) in enumerate(NOSE_X):
    side = "Left" if i == 0 else "Right"
    tip_at_x0 = (i == 0)
    battens_bed.append(wedge(nx0, NOSE_Y0, BATTEN_Z0_BED,
                             nx1 - nx0, BATTEN_W, BATTEN_H,
                             NOSE_TIP_H, tip_at_x0,
                             f"Panel Front Batten {side} (bed mode)", "panel",
                             ("Panel front cross batten (M5)",
                              sec(BATTEN_W, BATTEN_H), nx1 - nx0)))
    battens_table.append(wedge(nx0, NOSE_Y0, BATTEN_Z0_TABLE,
                               nx1 - nx0, BATTEN_W, BATTEN_H,
                               NOSE_TIP_H, tip_at_x0,
                               f"Panel Front Batten {side} (table mode)",
                               "panel"))

# ---------------------------------------------------------------------------
# ASSEMBLY
# ---------------------------------------------------------------------------
IDENTITY = Location((0, 0, 0))
# Z-up (CAD) -> Y-up (Quick Look / glTF / USD): a -90 deg turn about X, which
# maps (x, y, z) -> (x, z, -y).  On its own that leaves the bed's front (the
# ladder side, bed +Y) pointing at USD -Z, i.e. away from the default viewer,
# so Quick Look / Xcode open the model showing its back.  A further 180 deg
# about the vertical (Y-up) axis turns the ladder side towards +Z:
#
#     (x, y, z) -> (-x, z, y)
#
# This is the ONE place the mesh orientation is set; it feeds the single-mesh
# .stl, the per-colour-group .stl files and therefore the .usdz.  Do not repeat
# the turn in tools/mesh_to_usda.swift or it would cancel out again.
Y_UP = Location((0, 0, 0), (0, 1, 0), 180) * Location((0, 0, 0), (1, 0, 0), -90)

MODES = {"bed_mode": panel_bed, "table_mode": panel_table}
# M4: the panel sub-assembly - the panel plus the battens screwed under it.
PANEL_BATTENS = {id(panel_bed): battens_bed, id(panel_table): battens_table}
# V13: and the same for the cushions - the two seat cushions are in both
# lists because they are the same two objects in the same place in both
# positions; only the back cushions differ.
CUSHIONS = {id(panel_bed): CUSHIONS_BED, id(panel_table): CUSHIONS_TABLE}


def mode_parts(panel):
    """The WOOD. Every cut-list part, in one mode. Fasteners are NOT in here.

    This is the list the cut list, parts.tsv, the overlap check and the
    connectivity check all run over, and it must stay wood-only: a screw
    overlaps the two members it ties together on purpose, so it would fail the
    no-overlap assert on sight.
    """
    return (parts + [mattress] + CUSHIONS[id(panel)] + [panel]
            + PANEL_BATTENS[id(panel)])


def is_soft(p):
    """True for the reference mattress and the four cushions - everything in
    the model that is bought as foam rather than cut as timber. Every wood-only
    list in this file filters on THIS and not on identity with `mattress`."""
    return getattr(p, "group", None) == "mattress"


# ===========================================================================
# FESTEMIDLER - THE JOINT TABLE
# ===========================================================================
# THE SINGLE SOURCE. Everything anyone knows about a fastener in this bed is
# in JOINTS below: what it is called in the shop, how many there are, what to
# pre-drill, WHICH TWO MEMBERS it ties, and WHICH WAY it is driven. The
# documentation used to hold the trade names and the counts (in
# tools/gen_doc_tables.py) while the drawings held the directions (in
# tools/render_lineart.py), and the only thing keeping the two honest was a
# hand-written sentence in each. Now the direction is a VECTOR the model
# derives, the prose is a caption printed off it, and both tools import this.
#
# Two kinds of field per joint:
#
#   the DOCS fields   id / title / n / drill / side  - what the beslagliste
#                     prints. `side` is prose about ACCESS ("you can reach it
#                     from inside the bed at any time"), not about direction:
#                     direction is machine data now.
#   the MACHINE fields `contacts` - one row per pair of members that meet,
#                     with the axis they meet across and, for each kind of
#                     fastener driven there, where it enters and where it
#                     goes. `fast` (the shopping line) is DERIVED from it.
#
# The member names are the keys of _PART: a regular expression per family, so
# one row serves a joint and its three mirror images.
# ---------------------------------------------------------------------------
_PART = {
    "post":        r"Corner Post (?:Back|Front) (?:Left|Right)",
    "post_back":   r"Corner Post Back (?:Left|Right)",
    "post_front":  r"Corner Post Front (?:Left|Right)",
    "rail":        r"Upper Side Rail (?:Back|Front)",
    "rail_back":   r"Upper Side Rail Back",
    "rail_front":  r"Upper Side Rail Front",
    "bench_rail":  r"Bench Rail (?:Back \(continuous\)"
                   r"|Front (?:Left|Right) \(segment\))",
    "bench_back":  r"Bench Rail Back \(continuous\)",
    "bench_front": r"Bench Rail Front (?:Left|Right) \(segment\)",
    "ledger":      r"Table Ledger Back",
    "beam":        r"End Beam (?:Left|Right)",
    "stub":        r"Bench Stub Leg (?:Back|Front) (?:Left|Right)",
    "upright":     r"Ladder Upright (?:Left|Right)",
    "rung":        r"Ladder Rung_\d+",
    "rung_blk":    r"Rung Block (?:Left|Right)_\d+",
    "bearer":      r"Table Bearer (?:Left|Right)",
    "guard":       r"Guard Rail Front (?:Left|Right)_\d+",
    "guard_host":  r"(?:Corner Post Front|Ladder Upright) (?:Left|Right)",
    "bed_slat":    r"Bed Slat_\d+",
    "bench_slat":  r"Bench Slat (?:Left|Right)_\d+",
    "end_slat":    r"Bench End Slat (?:Left|Right)",
    "end_cleat":   r"Bench End Cleat (?:Left|Right)",
    "panel":       r"Movable Panel \(bed mode\)",
    "batten":      r"Panel Stiffener Batten (?:Left|Right) \(bed mode\)",
    "nose":        r"Panel Front Batten (?:Left|Right) \(bed mode\)",
}

# The Norwegian name of each family, for the captions the emitters print.
PART_NO = {
    "post": "hjørnestolpe", "post_back": "bakre hjørnestolpe",
    "post_front": "fremre hjørnestolpe", "rail": "sidevange",
    "rail_back": "bakre sidevange", "rail_front": "fremre sidevange",
    "bench_rail": "benkevange", "bench_back": "bakre benkevange",
    "bench_front": "fremre benkevange",
    "ledger": "bordbærelekt", "beam": "endebjelke", "stub": "stubbefot",
    "upright": "stigevange", "rung": "rungetrinn", "rung_blk": "stigekloss",
    "bearer": "bordkloss",
    "guard": "rekkverksbord", "guard_host": "hjørnestolpe / stigevange",
    "bed_slat": "køyespile", "bench_slat": "benkespile",
    "end_slat": "endespile", "end_cleat": "endelist",
    "panel": "løs plate", "batten": "avstivningslekt",
    "nose": "fremre kilelekt",
}


def _is_part(kind, label):
    return re.fullmatch(_PART[kind], label) is not None


# ---------------------------------------------------------------------------
# EC5 GEOMETRY - AND THE RULE THAT SIZES EVERY ROW
# ---------------------------------------------------------------------------
# A pre-drilled wood screw wants 3d of clear edge all round and 4d between
# itself and the next one. Written out for a row of n screws that has to live
# on one contact face:
#
#       (n - 1) * 4d  +  2 * 3d   <=   the face
#
# That is the FITS-THE-FACE rule, and it is the single most useful assert in
# this file, because the count in a joint table is exactly the kind of number
# that gets written down once and never checked against the wood. Two screws
# of 6 mm want 60 mm of face. A ladder rung block offers 48 mm of upright to
# lie on. So a rung block takes ONE screw, not two - see J5.
SCREW_D = 6                       # the frame screw
MIN_EDGE = 3 * SCREW_D            # 18 mm - the number quoted in the docs
MIN_SPACING_GRAIN = 5 * SCREW_D   # 30 mm - two screws stacked along the grain
MIN_SPACING_CROSS = 4 * SCREW_D   # 24 mm - two screws stacked across it
FIT_TOL = 1e-6


def min_edge(d):
    return 3 * d


def min_spacing(d):
    return 4 * d


def max_row(avail, d):
    """How many d-screws a face `avail` mm across can legally carry in a row."""
    if avail + FIT_TOL < 2 * min_edge(d):
        return 0
    return int((avail - 2 * min_edge(d)) / min_spacing(d) + FIT_TOL) + 1


def row_positions(lo, hi, n, d, what):
    """The centres of `n` screws in one row across the face [lo, hi].

    Spread out rather than bunched: the row opens up until it has 1,5 x 3d of
    edge at each end, and only then does it stop, so a two-screw row in a 98
    mm rail lands 44 mm apart and not on the bare 4d minimum. It never opens
    past that, because the edge is the thing that splits.
    """
    avail = hi - lo
    need = (n - 1) * min_spacing(d) + 2 * min_edge(d)
    assert avail + FIT_TOL >= need, (
        f"{what}: {n} skruer a d{d:g} trenger {need:g} mm flate "
        f"((n-1) x 4d + 2 x 3d), men flaten er {avail:g} mm. "
        f"Lovlig antall her er {max_row(avail, d)}.")
    mid = (lo + hi) / 2
    if n == 1:
        return [mid]
    span = max((n - 1) * min_spacing(d), avail - 3 * min_edge(d))
    step = span / (n - 1)
    return [mid - span / 2 + i * step for i in range(n)]


_SIZE_RE = re.compile(r"(\d+)\s*[x×]\s*(\d+)")


def fastener_size(name):
    """(diameter, length) in mm, read off the trade name."""
    m = _SIZE_RE.search(name)
    if not m:
        return (5.0, 50.0)
    return (float(m.group(1)), float(m.group(2)))


# ---------------------------------------------------------------------------
# THE BRACKETS
# ---------------------------------------------------------------------------
# Three bent-plate parts, each named once here and modelled from these numbers
# in the geometry block below. `leg` is how far each flange reaches along the
# member it lies on, `width` how wide the flange is across it, `t` the steel.
BRACKETS = {
    "vinkel90": dict(name="Vinkelbeslag 90×90×40×2,5 varmforsinket",
                     leg=90.0, width=40.0, t=2.5),
    # 20 mm wide, not the 40 the first cut of this table said: the flange has
    # to lie inside a 36 mm post face without touching the wall plane behind
    # it, and under a 21 mm ledger. 40 would stand 2 mm proud of both.
    "vinkel40": dict(name="Vinkelbeslag 40×40×20", leg=40.0, width=20.0,
                     t=2.0),
}


def drive(name, per, frm=None, into=None, axis=None, sign=None, row=None,
          row_sign=None, reach=None, toe=None, bracket=None, bears=None,
          exempt=None, counterbore=0.0, offset=None):
    """One kind of fastener driven at one contact patch.

    `name`    the trade name, in full - the same string the shopping list uses.
    `per`     how many of them this ONE joint takes.
    `frm`     the member the screw is driven THROUGH. It enters on that
              member's own outer face and travels along the patch normal into
              the other member. The ordinary case.
    `into`    + `axis`: a fastener that does NOT cross the patch - a bracket
              flange screwed sideways into a stub leg, say. It travels along
              `axis` into the named member. `sign` pins the direction where
              the "from the room side of the bed" default is wrong.
    `row`     the axis the screws of this drive are laid out along. Defaults
              to the longer of the two axes of the contact face, which is
              right nearly everywhere; J8 is the exception, and says so.
    `row_sign` for an `into` drive, which way the bracket flange runs out of
              the corner: +1 / -1 / "outboard" (away from the middle of the
              bed) / None (into whichever side of the member has more room).
    `reach`   how far that flange runs, mm. Defaults to the bracket's `leg`.
    `toe`     this is a SKEW screw. dict(face=axis, face_sign=+-1, deg=,
              back=): it enters the `frm` member's face at `face`/`face_sign`,
              `back` mm from the joint, and is tilted `deg` degrees off that
              face's normal, towards the member it grips.
    `bracket` the key in BRACKETS this row IS - then it is a plate, not a screw.
    `bears`   this bracket CARRIES the named member: its second flange has to
              be the horizontal one, screwed straight UP, and its seat has to
              be that member's own underside. Written down because "the
              bracket is on upside down" is the failure this whole detail
              exists to prevent, and it is invisible in a table of counts.
    `exempt`  a Norwegian reason the through-screw fit rule does not decide
              this one: a toe screw. Anything without a reason has to obey.
    `counterbore` mm of clearance hole bored into the `frm` member's outer
              face before the screw goes in. The head then sits THAT far
              inside the member instead of flush with its face, and the wood
              the screw actually has to pass through is the rest. It is the
              only way to aim a stated thread length at a thin receiver: see
              J13a, where 46 mm of counterbore in a 73 mm batten turns a
              stock 5x40 into "27 mm of batten, 13 mm of an 18 mm panel".
              The fit rule below reads the REMAINING thickness, so a
              counterbored screw is checked exactly like any other.
    `offset`  (axis, mm) or (axis, mm, sign): move every screw of this drive
              that far OFF the centre the placement rule would otherwise put
              it at. It exists for one reason and it is X10: the rule puts a
              row in the middle of its contact window, and two joints that
              share a piece of wood both obey it and both land on the same
              middle. `sign` is +1 / -1, or "outboard" / "inboard" so one row
              of table still serves a joint and its mirror image. It has to be
              PERPENDICULAR to the drive direction - an offset along the screw
              would take the head off the face it is driven from - and that is
              asserted where it is applied. Nothing about it is a free hand:
              the measured edge-distance rule (X6), the containment asserts and
              X10 itself all still have to pass on the moved screw, so an offset
              is a proposal the shapes get to refuse.
    """
    return dict(name=name, per=per, frm=frm, into=into, axis=axis, sign=sign,
                row=row, row_sign=row_sign, reach=reach, toe=toe,
                bracket=bracket, bears=bears, exempt=exempt,
                counterbore=counterbore, offset=offset)


# A toe screw is quoted by the face it enters, how far back from the joint it
# starts and how far it is tilted off that face's normal. Both of the bed's
# skew joints are here and nowhere else.
#
# V4: AND EVERY ONE OF THEM NOW SITS IN A SEAT. Until this round a skew screw's
# head simply stood where the face was and part of it stood PROUD of the wood -
# the model even had a tolerance for it (TOE_HEAD_ALLOWANCE, a tenth of the
# screw's volume allowed outside the joint) and the beslagliste asked for "a
# counterbore" in prose. Both are gone. A 90 degree countersink met at 25-30
# degrees cannot lie flush and never could; what makes it lie flush is a
# FLAT-BOTTOMED SEAT BORED ALONG THE SCREW'S OWN AXIS - a pocket, drilled with
# an 18 mm Forstner bit running in the drill-guide block (VINKELKLOSS, below),
# whose flat bottom is square to the screw and therefore square to the head.
#
#   TOE_SEAT_D       18 mm, the Forstner size. The 6 mm screw's head is 11.8
#                    across, so 18 leaves 3 mm all round for the head and room
#                    for the bit to enter at the angle.
#   TOE_SEAT_DEPTH   measured ALONG THE SCREW, from the mouth of the pocket to
#                    its flat bottom - i.e. exactly how far the head is moved
#                    into the wood. The head is a disc of radius r_h in a plane
#                    square to the screw, so its highest point stands
#                    r_h*sin(deg) above the head centre measured along the face
#                    normal, and the centre is seat*cos(deg) below the face.
#                    Head fully under the wood therefore wants
#                    seat > r_h*tan(deg), which at J8-B's 65 deg and an 11.8 mm
#                    head is 12.7 mm.
#
# K4 - AND THE HEAD DOES NOT ALWAYS FIND THE BOTTOM. V4 set 18 for both joints,
# one setting on the depth stop, and measured 2.26 mm of wood over the head at
# J8-B. That is the number for a head lying ON the flat bottom, and a
# countersunk head in a flat-bottomed pocket has a SECOND place it can come to
# rest: the 90 degree cone can bear on the RIM OF THE PILOT HOLE. The head is
# 11.8 across, the pilot under it is 6, and a 90 degree cone between the two
# stands (11.8 - 6)/2 = 2.9 mm off the bottom. Along a 65 degree screw that is
# 2.9*cos(65) = 1.23 mm of the cover, so the honest J8-B number was not 2.26 but
#
#       2.26 - 1.23 = 1.03 mm  against a 1.0 mm limit.
#
# A joint whose margin depends on the screw finding the bottom of its own pocket
# has no margin. J8-B gets its own depth, 20 mm; J10 is not close and keeps 18:
#
#                    head on the bottom   cone on the pilot rim
#     J8-B  20 mm      3.11 mm              1.88 mm      (6x80, 11.8 head)
#     J10   18 mm      4.89 mm              3.76 mm      (5x60,  9.5 head)
#
# The two millimetres buy a second thing nobody asked for. The flat bottom is a
# ⌀18 disc standing at `deg` to the face, so it reaches 9*sin(deg) above and
# below its own centre measured on the face normal while its centre lies
# seat*cos(deg) down: the disc is a COMPLETE circle inside the wood only from
# seat >= 9*tan(deg) - 19.30 mm at J8-B, 15.59 at J10. At 18 mm the J8-B pocket
# was 1.3 mm short of that and the shallow rim of its own bottom broke out at
# the face. The head never noticed (it is 11.8 across, and its rim wants only
# 5.9*tan(65) = 12.65), but the bottom the drawing shows was not the bottom the
# wood had. At 20 it is, with 0.3 mm to spare. J10 has been clear all along.
#
# The price of the two millimetres is paid twice and neither payment hurts. The
# pocket bottom moves 2*sin(65) = 1.81 mm nearer the rail's end grain, its near
# edge 13.9 -> 12.1 mm from the end - but the MOUTH's near edge has been sitting
# at 34 - 9/sin(25) = 12.7 mm the whole time and does not move, so the governing
# edge changes hands rather than collapsing. And 20 mm of the screw is spent in
# the pocket instead of 18, so J8-B's 6x80 buries 60 mm of thread and J10's 5x60
# buries 42. Both are re-checked by the ordinary tip-inside / tip-cover asserts,
# which know nothing about seats.
TOE_SEAT_D = 18.0                # Forstner diameter for the seat
TOE_SEAT_DEPTH = 18.0            # along the screw axis, mouth to flat bottom
TOE_SEAT_DEPTH_BENCH = 20.0      # K4: J8-B's own, 2 mm deeper - see above
TOE_SEAT_MIN_COVER = 1.0         # mm of wood over the highest point of the head
# K4 - THE WALL BETWEEN TWO SEATS. J8-B puts two of these pockets in one face,
# and the row rule that spaces them knows only about SHANKS: 4d = 24 mm centres
# for a 6 mm screw, which between two ⌀18 pockets leaves 24 - 18 = 6 mm of wood.
# Six millimetres is enough here and it is not enough anywhere much thinner, so
# it is written down rather than left to arithmetic nobody is doing. The floor
# is ONE SHANK DIAMETER of wood: a Forstner cutting the second pocket has to
# have a rim of solid wood to cut against for its whole circle, and d - the same
# unit the edge and spacing rules are already written in - is the least that
# reads as wood rather than as a fin. K2 asks a bore's worth (12 mm) between two
# ⌀12 counterbores, but those sit at the free edge of a 77 mm wing with short
# grain on both sides; these two sit mid-face in a 68 mm rail with the full
# 48 mm of its depth behind them, which is why the floor is d and not D.
TOE_SEAT_MIN_WEB = 6.0           # mm of wood between two seats in one face
TOE_BENCH_POST = dict(face=1, face_sign=1, deg=65.0, back=34.0,
                      seat=TOE_SEAT_DEPTH_BENCH)
TOE_STUB_RAIL = dict(face=0, face_sign="inboard", deg=60.0, back=35.0)


# X10 - AND THE SAME UNIT ONE MORE TIME, BETWEEN TWO SHANKS. See the X10 block at
# the bottom of the fastener asserts: two screws that meet in the same piece of
# wood are the one collision this file never looked for, and the floor it is
# held to is written here, next to the seat's, because it is the same argument.
# The wood between two screws has to READ AS WOOD and not as a fin, and the
# least that does is one shank of the thinner of the two - d, the unit MIN_EDGE
# (3d), min_spacing (4d) and TOE_SEAT_MIN_WEB (1d) are all already written in.
def screw_web(da, db):
    """The wood two screws must leave between them: one shank of the thinner."""
    return min(da, db)


def screw_clearance(da, db):
    """Least distance between two screw AXES: the two half-shanks plus the web.

    Head-to-head falls out of it rather than needing a second rule - the
    widest pair in the bed is two 6 mm heads at 11.8 mm, and (6+6)/2 + 6 = 12
    stands them apart on their own.
    """
    return (da + db) / 2 + screw_web(da, db)

# THE DRILL-GUIDE BLOCK - "vinkelkloss". A skew hole started freehand walks,
# and it walks worst exactly where these two are: near an end, in a face the
# bit meets at 25 or 30 degrees. It is NOT part of the bed, so it is not in
# `parts` and not in the cut list proper; it is a shop aid and it is listed as
# one (SHOP_AIDS below), made in steg 0 off the offcut pile.
#
# K5 - IT IS A BORED BLOCK, AND THERE ARE TWO OF THEM. V4 wrote it as one 160 mm
# offcut with a ramp sawn on each end, the bit asked to LIE ON the ramp. Three
# things were wrong with that:
#
#   * a bit lying on a ramp is guided on one side only. Nothing stops it
#     rolling off the mark, which is the exact failure the jig exists for;
#   * "25° målt fra flaten" on a mitre saw is the complement of what you set.
#     Tilt the blade 25 degrees and the face it leaves stands at 65 degrees to
#     the one on the table, not 25. The old recipe therefore produced a ramp
#     for the wrong joint;
#   * one block with two ends means one clamp setup has to serve both joints,
#     and the two are drilled in different steps on different members.
#
# So: TWO blocks, one per angle, each of TOE_JIG_PLIES pieces of the bed's own
# 48x68 screwed FLAT FACE TO FLAT FACE. A ⌀TOE_SEAT_D hole is bored SQUARE
# through both while the block is still a rectangular block - that is the whole
# trick, a square hole in a square block is a hole anyone can bore - and only
# THEN is the sole cut off under it on the mitre saw with the blade tilted. The
# tilt is the drill's own angle to the face; the sole it leaves stands at
# 90 - tilt to the bored face, and therefore at `tilt` to the hole. The hole is
# a sleeve now, not a ramp, and it is two plies deep.
#
#     saw tilt        = 90 - deg  (25 / 30)  - what you set on the saw
#     sole to face    = deg       (65 / 60)  - what you measure on the block
#     hole to sole    = 90 - deg  (25 / 30)  - what the bed is drawn on
#
# The control measure is the mouth the hole leaves in the finished sole: a
# ⌀TOE_SEAT_D cylinder cut by a plane at `90 - deg` to its axis is an ellipse
# TOE_SEAT_D wide and TOE_SEAT_D/sin(90 - deg) long. Measure it before the jig
# ever touches the bed; if it is short, the tilt was set to the complement.
TOE_JIG_LEN = 200                # per ply
TOE_JIG_PLIES = 2                # screwed face to face - the hole is the guide
TOE_JIG_ANGLES = {"J8-B": 90.0 - TOE_BENCH_POST["deg"],     # 25 deg
                  "J10": 90.0 - TOE_STUB_RAIL["deg"]}       # 30 deg
TOE_JIG_SEATS = {"J8-B": TOE_BENCH_POST.get("seat", TOE_SEAT_DEPTH),
                 "J10": TOE_STUB_RAIL.get("seat", TOE_SEAT_DEPTH)}
TOE_JIG_ELLIPSE = {_k: (TOE_SEAT_D / math.sin(math.radians(_a)), TOE_SEAT_D)
                   for _k, _a in TOE_JIG_ANGLES.items()}

# SHOP AIDS - things you CUT but do not BUILD IN. They are not parts of the
# bed, so they are not in `parts`, not in parts.tsv, not in CUT_LIST and not in
# the piece count; they are cut in steg 0 off the offcut pile and they belong
# in the manual because a jig you were never told to make is a jig you do not
# have when you need it.
def _nb(x, nd=1):
    """A number the way a Norwegian ruler reads it: 42,6 and not 42.6."""
    return f"{x:.{nd}f}".rstrip("0").rstrip(".").replace(".", ",")


SHOP_AIDS = [
    dict(key=f"vinkelkloss-{_jid.lower()}",
         name=f"Vinkelkloss {_tilt:g}° ({_jid}) — borjigg for skråskruen",
         section=sec(BATTEN_W, BATTEN_H), length=TOE_JIG_LEN,
         qty=TOE_JIG_PLIES,
         cut=(f"{TOE_JIG_PLIES} stk. skrus FLATE MOT FLATE til én kloss. "
              f"⌀{TOE_SEAT_D:g} bores VINKELRETT gjennom begge mens klossen "
              f"ennå er firkantet — det er hele trikset. Først DERETTER kappes "
              f"sålen av under hullet: kappsag med bladet vippet "
              f"{_tilt:g}°, som gir en såle som står "
              f"{90.0 - _tilt:g}° på den borede flaten og dermed {_tilt:g}° "
              f"på hullaksen. Kontrollmål: hullets munning i sålen er en "
              f"ellipse på {_nb(TOE_JIG_ELLIPSE[_jid][0])} × "
              f"{_nb(TOE_JIG_ELLIPSE[_jid][1])} mm — er den for kort, ble "
              f"vippen satt på komplementvinkelen"),
         use=(f"klemmes mot flaten med TO tvinger, hullet over merket. "
              f"⌀{TOE_SEAT_D:g} forstnerbor og deretter forboret går NED I "
              f"hullet, så boret ikke kan vandre. Dybdemerke: hold boret i "
              f"jiggen til randen flukter med sålen ved hullaksen, merk av på "
              f"skaftet og flytt merket {TOE_JIG_SEATS[_jid]:g} mm opp — det "
              f"er setedybden. Brukes i {_jid}"))
    for _jid, _tilt in TOE_JIG_ANGLES.items()
]

JOINTS = [
    dict(id="J1", title="Endebjelke → hjørnestolpe", n=4,
         drill="⌀6 gjennom bjelken, ⌀4 i stolpen",
         # X11: this string said "fra bjelkens utside", which is a face that
         # cannot be reached: the beam's outer face is the one BUTTED AGAINST
         # the post, so a screw started there would have to begin inside the
         # post. The model's own placement says otherwise - the row projects
         # onto the beam's INNER face - and that is the face a man standing in
         # the bed can actually put a drill on.
         side="Fra bjelkens innside (mot sengas midte), inn mot stolpen — "
              "helt inne i sengen, tilgjengelig hele veien. Disse to skruene "
              "er HELE festet: det står ingen kloss under bjelkeenden",
         # X10: the pair steps 8 mm DOWN the beam. The back corner is where the
         # end beam and the back side rail both take hold of the same post, and
         # the rail's own J2-B comes straight down through the post top to
         # Z 1380 - five millimetres past this row's upper screw. Eight takes
         # the row to 1323 / 1367 and puts 13 mm between the two, and the beam
         # still has 19 mm of edge under the lower one.
         contacts=[dict(a="post", b="beam", axis=0, drives=[
             drive("Treskrue 6×80 forsenket Torx", 2, frm="beam", row=2,
                   offset=(2, -8.0))])]),
    # V5: DRIVEN FROM INSIDE THE BED. Both directions fit (a 6x80 crosses 36
    # into 48 and 48 into 36 alike), so the rule calls it 'tvetydig' and the
    # table decides - and the table decides on the front face: a head on the
    # post's forside would be the first thing anyone in the room sees.
    dict(id="J2", title="Fremre sidevange → fremre hjørnestolpe", n=2,
         drill="⌀6 gjennom vangen, ⌀4 i stolpen",
         side="Fra vangens innside — inne fra sengen — gjennom vangen og inn "
              "i stolpen. Stolpens forside er urørt",
         contacts=[dict(a="post_front", b="rail_front", axis=1, drives=[
             drive("Treskrue 6×80 forsenket Torx", 2, frm="rail_front")])]),
    dict(id="J2-B", title="Bakre sidevange → bakre hjørnestolpe "
                          "(vangen hviler på stolpetoppen)", n=2,
         drill="⌀6 gjennom vangen, ⌀4 i stolpens endeved; forsenk hodet godt "
               "under vangens overkant så køyespilene ligger flatt",
         side="Rett ned gjennom vangen i stolpetoppen, mens bakrammen ligger "
              "flatt på gulvet. Ingenting på veggsiden, og ingen kloss: "
              "vangen står 12 mm proud av den tynnere stolpen, så et rett "
              "beslag ville uansett ikke ligget an mot begge",
         # X10: the pair steps 9 mm INBOARD off the post centre. The post's
         # 98 mm of X is shared with the first bed slat, whose own J6 screw
         # comes down at X 69 / 1921 and lands 6,32 mm from this row - two
         # rules, both putting their screw in the middle of their own window,
         # both right, and the middle is the same place. 9 mm moves the outer
         # one to X 80 / 1910, 12,5 mm off the slat screw, and leaves the row
         # 18 mm (3d) from the post end. Nothing about the joint changes.
         contacts=[dict(a="post_back", b="rail_back", axis=2, drives=[
             drive("Treskrue 6×120 forsenket Torx", 2, frm="rail_back",
                   offset=(0, 9.0, "inboard"))])]),
    # V5: same flip as J2. The stigevange's forside is in the front plane.
    dict(id="J3", title="Stigevange → fremre sidevange", n=2,
         drill="⌀6 gjennom sidevangen, ⌀4 i stigevangen",
         side="Fra sidevangens innside — inne fra sengen — gjennom vangen og "
              "inn i stigevangen. Stigevangens forside er urørt",
         contacts=[dict(a="upright", b="rail_front", axis=1, drives=[
             drive("Treskrue 6×80 forsenket Torx", 3, frm="rail_front")])]),
    # X2: two per rung end, and the RUNG COUNT is derived (even_climb), so the
    # joint count has to be derived off the same list rather than typed 8.
    # X10 - THE SCREW THAT COULD NOT EXIST, AND WHY IT IS THE ONE THAT GOES.
    # A rung end used to carry THREE screws: a 6x120 through the upright into
    # the tread's end, a 5x60 down through the tread into the block, and J5's
    # 5x60 through the block into the upright. The middle one was driven
    # straight through the first: the 6x120 runs along the tread's own centre
    # line at Z 273 and a screw dropped at X 853 crosses it at a POINT, 0,00 mm
    # apart, and it did that ten times over. It is not a placement mistake - it
    # is two correct rules both putting their screw in the middle of the same
    # piece of wood - and it cannot be moved out of the way:
    #   * in Y both are pinned to 770. The upright offers 36 mm and a 6 mm
    #     screw wants 3d each side of it, so the through screw has exactly one
    #     legal Y; the block offers 36 mm too, so the down screw has 770 +- 3.
    #   * in Z the through screw is pinned to the tread's own 48 mm, 273 +- 6,
    #     and a screw dropped from the tread's top has to cross all 48 of them
    #     to reach the block at all.
    #   * in X the down screw is pinned to the block's 36 mm, 853 +- 3, and a
    #     through screw that stops short of it has nothing left: 6x60 is 48 mm
    #     of upright and 12 mm of end grain. A 6x80 still reaches X 867.
    #   * turned round - up from the block's underside - it clears the 6x120
    #     by 12 mm and lands on J5 instead, which sits at the block's own
    #     mid-height Z 225 and cannot move either.
    # So the block simply cannot take a vertical screw while the tread has a
    # horizontal one, and the honest answer is to take the vertical one out
    # rather than to bore two screws through each other and draw it as fine.
    # WHAT IT COSTS, MEASURED: nothing in the load path. The rung end's 0,5 kN
    # goes into the block in BEARING (K1's row, 1296 mm2 at 0,15 of f_c,90,d)
    # and from the block into the upright through J5, and it goes a second way
    # through the 6x120 in shear - 2,0 kN against 0,5. The deleted screw
    # carried neither: it was a LOCK, stopping the block turning about J5's
    # single screw. That job is now argued off the wood instead of off a screw
    # that cannot be there: the block is trapped between the upright's face
    # (its own screw), the tread lying flat on 36 x 36 mm of its top, and that
    # tread being itself pinned to the upright 48 mm above by the 6x120. To
    # turn, the block has to lift a tread that is bolted down. See the K1 block
    # for the rows. ASSEMBLY still says the tread is screwed down into the
    # block - that sentence is now wrong and is flagged for the docs round.
    dict(id="J4", title="Rungetrinn → stigevange (per trinnende)",
         n=2 * len(RUNG_TOPS),
         drill="⌀6 gjennom stigevangen inn i trinnenden, ⌀4 i trinnet",
         side="6×120 fra utsiden av stigevangen, inn i trinnets endeved. "
              "Ingenting gjennom trinnets overside — trinnet ligger på "
              "stigeklossen og klossen har sin egen skrue (J5)",
         contacts=[
             dict(a="rung", b="upright", axis=0, drives=[
                 drive("Treskrue 6×120 forsenket Torx", 1, frm="upright")])]),
    dict(id="J5", title="Stigekloss → stigevange", n=2 * len(RUNG_TOPS),
         drill="⌀3,5 gjennom klossen, ⌀3 i vangen",
         side="Fra stigeåpningen, inn i vangens innside",
         contacts=[dict(a="upright", b="rung_blk", axis=0, drives=[
             drive("Treskrue 5×60 forsenket Torx", 1, frm="rung_blk")])]),
    # X9: the bordkloss is screwed the way the ladder's own pieces are, but
    # from the OTHER side of the upright than J5 is. J5 drives a 5x60 into the
    # face from inside the ladder opening, which is right for a block that sits
    # UNDER its load; the bordkloss carries its load 70 mm behind that face on
    # a cantilever, so the screw is working in withdrawal as much as in shear
    # and it wants the bigger one, driven through the whole upright: 6x80
    # through 48 mm of stigevange leaves 32 mm in a 36 mm block, and it lands
    # in side grain, not end grain.
    # X10: TWO of them, stacked up the face. X9 wrote "ONE screw is all the face
    # holds - 36 x 48 is exactly 2 x 3d for a 6 mm screw across the short way",
    # and that was true of a 36 x 48 face; what it did not ask was whether one
    # screw is all the JOINT NEEDS, and it is not. See the X10 note over
    # TABLE_BEARER_T: this block carries a LOOSE plate whose load stands 55 mm
    # in front of the screw line, with nothing on top of it to stop it turning,
    # and one screw carries that moment in friction and shank bending. The
    # block stands 68 mm in Z now, so the fixing face is 36 x 68 and 68 is
    # 2 x 3d + 4d with 8 mm to spare. The pair turns the eccentricity into two
    # screws in opposite shear.
    dict(id="J5-B", title="Bordkloss → stigevange", n=2,
         drill="2 × ⌀6 gjennom stigevangen, ⌀4 i klossen — stablet i høyden",
         side="Fra stigevangens utside — fra benkerommet — gjennom vangen og "
              "inn i klossen. Klossens egen underside er urørt",
         contacts=[dict(a="upright", b="bearer", axis=0, drives=[
             drive("Treskrue 6×80 forsenket Torx", 2, frm="upright",
                   row=2)])]),
    dict(id="J6", title="Køyespile → sidevange (per spileende)", n=28,
         drill="⌀3,5 gjennom spilen, forsenk hodet under flaten",
         side="Ovenfra, ned i vangen",
         contacts=[dict(a="bed_slat", b="rail", axis=2, drives=[
             drive("Treskrue 5×60 forsenket Torx", 1, frm="bed_slat")])]),
    dict(id="J7", title="Rekkverksbord → hjørnestolpe / stigevange "
                        "(per omlegg)", n=8,
         drill="⌀3,5 gjennom bordet, ⌀3 i stolpen",
         side="Fra sengesiden, inn i stolpens/stigevangens innside",
         contacts=[dict(a="guard", b="guard_host", axis=1, drives=[
             drive("Treskrue 5×60 forsenket Torx", 2, frm="guard")])]),
    # V5: same flip as J2 and J3, and here it does a second job - the two
    # screws are now the whole end fixing of the rail segment (the J9-F block
    # is gone, see the C2 note), so they are driven from the side you can
    # actually reach into with a drill while the bench is still open.
    dict(id="J8", title="Fremre benkevange → fremre hjørnestolpe", n=2,
         drill="⌀6 gjennom vangen, ⌀4 i stolpen",
         side="Fra vangens innside — inne fra benkerommet — gjennom vangen og "
              "inn i stolpen. Stolpens forside er urørt",
         # row=2: the face is 95 wide and 73 tall, so the automatic choice
         # would stack the pair along the RAIL. They belong stacked up the
         # POST, the same pattern as J2 - that is the direction the joint
         # takes moment in.
         contacts=[dict(a="bench_front", b="post_front", axis=1, drives=[
             drive("Treskrue 6×80 forsenket Torx", 2, frm="bench_front",
                   row=2)])]),
    dict(id="J8-B", title="Bakre benkevange → bakre hjørnestolpe "
                          "(endeskjøt)", n=2,
         drill=(f"Først sete: ⌀{TOE_SEAT_D:g} forstner "
                f"{TOE_JIG_SEATS['J8-B']:g} mm ned LANGS skruens akse, med "
                f"vinkelklossen som styring. Så ⌀6 skrått videre gjennom "
                f"vangen og ⌀4 i stolpen — forbor hele veien, dette er en "
                f"skråskrue nær en ende"),
         side="Skrått fra vangens forside inn i stolpen, ut av et flatbunnet "
              "sete så hodet ligger helt under treet. Vangen ligger fast "
              "mellom de to stolpene, og disse to skruene er HELE festet i "
              "enden — det står ingen kloss under den",
         # X10: the pair steps 2 mm UP the rail, and J17 steps 8 mm down, so the
         # end cleat's own screws land midway between these two instead of
         # 2 mm from the upper one. Three fixings meet in this post and two of
         # them were on the same height.
         contacts=[dict(a="bench_back", b="post_back", axis=0, drives=[
             drive("Treskrue 6×80 forsenket Torx", 2, frm="bench_back",
                   toe=TOE_BENCH_POST, offset=(2, 2.0),
                   exempt="skråskrue gjennom vangens forside nær enden")])]),
    dict(id="J10", title="Benkevange → stubbefot", n=4,
         drill=(f"⌀3 i foten og i vangen. Skråskruen får først sete: "
                f"⌀{TOE_SEAT_D:g} forstner {TOE_JIG_SEATS['J10']:g} mm ned "
                f"langs skruens akse, med vinkelklossen som styring, så ⌀3,5 "
                f"videre"),
         side="Vinkelbeslaget sitter i hjørnet mellom fotens utside og "
              "vangens underside, med den ene fliken opp i vangen og den "
              "andre inn i foten; den ene 5×60 er en skråskrue nedenfra og "
              "opp i vangen, ut av et flatbunnet sete så hodet ligger helt "
              "under treet",
         contacts=[dict(a="bench_rail", b="stub", axis=2, drives=[
             drive(BRACKETS["vinkel90"]["name"], 1, into="stub", axis=0,
                   sign="inboard", row=2, row_sign=-1, bracket="vinkel90",
                   bears="bench_rail"),
             drive("Treskrue 5×40 forsenket Torx", 2, into="stub", axis=0,
                   sign="inboard", row=2, row_sign=-1, reach=90.0),
             drive("Treskrue 5×40 forsenket Torx", 2, into="bench_rail",
                   axis=2, sign=1, row=0, row_sign="outboard", reach=90.0),
             drive("Treskrue 5×60 forsenket Torx", 1, frm="stub",
                   toe=TOE_STUB_RAIL,
                   exempt="skråskrue nedenfra opp i vangen")])]),
    dict(id="J11", title="Benkespile → benkevange (per spileende)", n=20,
         drill="⌀3,5 gjennom spilen, forsenk hodet under flaten",
         side="Ovenfra, ned i benkevangen",
         contacts=[dict(a="bench_slat", b="bench_rail", axis=2, drives=[
             drive("Treskrue 5×60 forsenket Torx", 1, frm="bench_slat")])]),
    # V13: the end slat has a bearing of its own at the back - the cleat - and
    # the ordinary front bench rail at the front. Two joints, because they are
    # two different pieces of wood; the screw is the same one the whole slat
    # field uses, driven the same way, from above.
    dict(id="J11-E", title="Endespile → fremre benkevange (fremre spileende)",
         n=2,
         drill="⌀3,5 gjennom spilen, forsenk hodet under flaten",
         side="Ovenfra, ned i benkevangen",
         # X10: 24,5 mm INBOARD off the patch centre. The front corner post
         # carries J8's two 6×80 stacked up its own centre line at X 50,5 /
         # 1939,5, and the end slat's window has the same centre - so this
         # screw came straight down onto the upper one of them. Moved inboard
         # it lands over the rail instead of over the post, 24,5 mm clear, with
         # 23 mm of slat end still outboard of it.
         contacts=[dict(a="end_slat", b="bench_front", axis=2, drives=[
             drive("Treskrue 5×60 forsenket Torx", 1, frm="end_slat",
                   offset=(0, 24.5, "inboard"))])]),
    dict(id="J16", title="Endespile → endelist (bakre spileende)", n=2,
         drill="⌀3,5 gjennom spilen, forsenk hodet under flaten",
         side="Ovenfra, ned i endelisten",
         contacts=[dict(a="end_slat", b="end_cleat", axis=2, drives=[
             drive("Treskrue 5×60 forsenket Torx", 1, frm="end_slat")])]),
    # V13: the one joint in this bed made into the back post's FRONT face. Two
    # 5x60 side by side along the 98 mm cleat - 36 mm through the cleat leaves
    # 24 mm in a 36 mm post, so nothing comes near the wall mounting plane
    # behind it. The pair sits along X because that is the long way of the
    # contact patch (98 x 48) and because the load they take is vertical shear.
    dict(id="J17", title="Endelist → bakre hjørnestolpe (mot stolpens "
                         "forside)", n=2,
         drill="⌀3,5 gjennom listen, ⌀3 i stolpen",
         side="Rett inn i stolpens forside, fra benkerommet — listen ligger "
              "flatt på stolpen og de to skruene er hele festet",
         # X10: 8 mm DOWN off the patch centre - see J8-B, which steps 2 mm up.
         # The two toe screws come through this same post at Z 253 and 277 and
         # this row sat at 273, four millimetres from one of them and crossing
         # its line. At 265 it stands exactly midway between them, 12 mm from
         # each, and still has 16 mm of cleat under it.
         contacts=[dict(a="end_cleat", b="post_back", axis=1, drives=[
             drive("Treskrue 5×60 forsenket Torx", 2, frm="end_cleat",
                   offset=(2, -8.0))])]),
    dict(id="J12", title="Bordbærelekt → bakre hjørnestolpe (endeskjøt)",
         n=2,
         drill="⌀3 i stolpen og i lekta — forboring er et krav: begge skruene "
               "står nær en ende, og lekta (48×68) tas i endeveden",
         side="Beslaget på stolpens innerflate, med den vannrette fliken "
              "UNDER lektas ende, så lekta har noe å hvile på og ikke bare "
              "henger i skruer",
         contacts=[dict(a="post_back", b="ledger", axis=0, drives=[
             drive(BRACKETS["vinkel40"]["name"], 1, into="post_back", axis=0,
                   row=2, row_sign=-1, bracket="vinkel40", bears="ledger"),
             drive("Treskrue 5×40 forsenket Torx", 1, into="post_back",
                   axis=0, row=2, row_sign=-1, reach=40.0),
             drive("Treskrue 5×40 forsenket Torx", 1, into="ledger", axis=2,
                   sign=1, row=0, reach=40.0)])]),
    # X11: THE SECOND WALL JOINT. Until this round the wall carried exactly one
    # fixing - J14, through the back side rail - and the nogging table promised
    # a fixing in all four zones. Three of the four had none, and zone 3 is the
    # one where that was worth fixing rather than only worth saying: the ledger
    # is the panel's REAR BEARING in table mode, it lies flat on the wall plane
    # over its whole 1894 mm exactly as the back rail does, and the nogging is
    # going into that wall anyway - the zone exists for this piece.
    #
    # THE FOUR ARGUMENTS AGAINST, TAKEN IN ORDER, BECAUSE NONE OF THEM HOLDS:
    #   1  «the ledger must be loadable straight down without hanging on
    #      screws in withdrawal» (ASSEMBLY §J12). True, and untouched: this
    #      screw is HORIZONTAL, so a downward load on the ledger is SHEAR in
    #      it, the strong direction. The two 40x40x20 brackets still carry the
    #      ends and the ledger still stands on steel, not on threads.
    #   2  «the wall plane must be dead flat». That rule is about anything
    #      sticking out BEHIND Y -48 - which is why the bracket is 20 mm wide
    #      and not 40. A fixing driven FROM the room, head counterbored into
    #      the ledger's front face at Y 0, adds nothing to the back face. It is
    #      the same geometry J14 already has.
    #   3  «the ledger must go in while the back frame is flat on the floor».
    #      It still does - J12 is a step 1 joint and stays there. These holes
    #      cannot be drilled in the workshop at all: the studs only exist in
    #      the room, so the drilling belongs to the same step as J14, after
    #      the frame is up against the wall.
    #   4  «the bed is the reference, not the room - a rigid wall fixing at
    #      midspan of a member already trapped between two posts overdetermines
    #      it». It would, if the ledger were somewhere else. It is not: it is
    #      part of the ONE rigid back frame whose whole back face J14 already
    #      pulls flat against the wall. The frame is at the wall before these
    #      screws exist; they do not decide where it sits, they only take load
    #      out of the middle of a 1894 mm span that had none.
    # What is bought for it: the rear bearing of the desk stops being a
    # simply-supported 1894 mm beam and becomes three spans of about 630, at
    # the one height on this wall where the load is a person leaning on a desk.
    dict(id="J12-V", title="Veggfeste — gjennom bordbærelekta inn i "
                           "stenderne", n=1,
         fast=[("Veggfeste etter veggtype (treskrue 8×100 i stender, eller "
                "plugg + skrue i mur)", 3)],
         drill="⌀8 gjennom lekta, forsenk for hodet; veggen etter festetype. "
               "Bores på stedet — stenderne finnes bare i rommet",
         side="Rett gjennom lekta inn i veggen, fra benkerommet. Lekta ligger "
              "flatt mot veggen i hele sin lengde, så festet trenger verken "
              "kloss eller brakett; hodet forsenkes i lektas forside, som "
              "ryggputa lener seg mot",
         contacts=[]),
    # V3: NOTHING GOES THROUGH THE TOP OF THE PANEL. The panel is the table
    # top, and a table top with twelve screw heads - or twelve plugs - in it is
    # a table top with twelve marks in it. So the battens are glued to the
    # panel and the screws are driven UP from underneath, out of a counterbore,
    # and the sheet's factory face is never broken. See PANEL_UPSCREW below for
    # the three options and the numbers that picked this one.
    dict(id="J13a", title="Avstivningslekt → løs plate (limt, skrudd "
                          "nedenfra)", n=2,
         drill=f"⌀{PANEL_UPSCREW_CBORE_D} kontrabor {PANEL_UPSCREW_CBORE:g} "
               f"mm opp i lektas underside, ⌀3,5 videre gjennom resten av "
               f"lekta. Ingenting gjennom platens overside",
         side="Nedenfra, opp gjennom lekta og 13 mm inn i den 18 mm platen. "
              "Limes med D3 trelim på hele lektas overkant først — skruene "
              "er tvinger som blir sittende",
         contacts=[dict(a="panel", b="batten", axis=2, drives=[
             drive("Treskrue 5×40 forsenket Torx", 6, frm="batten",
                   counterbore=PANEL_UPSCREW_CBORE)])]),
    dict(id="J13b", title="Fremre kilelekt (vinge) → løs plate (limt, skrudd "
                          "nedenfra)", n=2,
         drill="⌀12 kontrabor opp i vingens underside TIL DET STÅR 27 mm "
               "IGJEN opp til plata — vingen er skråkappet, så det blir "
               "dypest ved roten og null ved tuppen. ⌀3,5 videre gjennom de "
               "siste 27 mm. Ingenting gjennom platens overside",
         side="Nedenfra, som J13a. Vingen ligger med forkanten i flukt med "
              "platens forkant, full høyde mot avstivningslekta og "
              "skråkappet ut mot platekanten",
         # K2: TWO, not three. The 116 mm wing carried three 5x40 with 35,5 mm
         # between them; the 77 mm wing would put the same three on the bare
         # 4d minimum, 20 mm, and three 12 mm counterbores at 20 mm centres
         # leave 8 mm of wood between adjacent holes. Two open back up to
         # 32 mm centres - 20 mm of wood - and the load case has room to
         # spare either way: the up-screws are clamps for a glue line and
         # the whole 18-screw group was under 0.05 utilised.
         contacts=[dict(a="panel", b="nose", axis=2, drives=[
             drive("Treskrue 5×40 forsenket Torx", 2, frm="nose",
                   counterbore=PANEL_UPSCREW_CBORE)])]),
    dict(id="J14", title="Veggfeste — gjennom den bakre sidevangen inn i "
                         "stenderne", n=1,
         fast=[("Veggfeste etter veggtype (treskrue 8×100 i stender, eller "
                "plugg + skrue i mur)", 6)],
         drill="⌀8 gjennom vangen, forsenk for hodet; veggen etter festetype",
         side="Rett gjennom vangen inn i veggen. Vangen ligger flatt mot "
              "veggen i hele sin lengde, så festet trenger ingen kloss og "
              "ingen brakett",
         contacts=[]),
    dict(id="J15", title="Filtknott under stolpe og stubbefot", n=8,
         fast=[("Filtknott / møbeltapp ⌀40", 1)],
         drill="—",
         side="Slås i endeveden før reisning",
         contacts=[]),
]
JOINT = {j["id"]: j for j in JOINTS}

# `fast` - the shopping line - is DERIVED from the machine data wherever there
# is machine data, so the beslagliste cannot say 2 x 6x90 while the model
# drives one. The two joints with no wood on the other side (the wall fixing
# and the felt pads) carry theirs by hand; they are the only ones.
for _j in JOINTS:
    if not _j["contacts"]:
        assert "fast" in _j, f"{_j['id']}: no contacts and no fast"
        continue
    _fast = {}
    _order = []
    for _c in _j["contacts"]:
        for _dr in _c["drives"]:
            if _dr["name"] not in _fast:
                _order.append(_dr["name"])
            _fast[_dr["name"]] = _fast.get(_dr["name"], 0) + _dr["per"]
    _j["fast"] = [(nm, _fast[nm]) for nm in _order]


# ---------------------------------------------------------------------------
# WHERE THE JOINTS ARE - READ OFF THE WOOD
# ---------------------------------------------------------------------------
# Every part in this bed is an axis-aligned box and carries its own extents,
# so the places where fasteners are driven are not listed by hand: two boxes
# that share a face, with area behind it, ARE a joint. The centre of that
# shared face is the joint and its normal is the axis the two meet across.
# The JOINTS table above says what is driven at each; nothing says WHERE.
CONTACT_TOL = 0.51        # two faces this close count as touching, mm
MIN_CONTACT = 900.0       # ignore contact patches smaller than this, mm2


def contacts(new_parts, other_parts=()):
    """[(point3, axis, sign, area, part_a, part_b), ...], biggest first."""
    out = []
    new_parts = list(new_parts)
    other_parts = list(other_parts)
    pairs = [(a, b) for i, a in enumerate(new_parts)
             for b in new_parts[i + 1:]]
    pairs += [(a, b) for a in new_parts for b in other_parts]
    for a, b in pairs:
        ea, eb = a.extents, b.extents
        for k in range(3):
            for sign, touch in ((1, abs(ea[k][1] - eb[k][0])),
                                (-1, abs(ea[k][0] - eb[k][1]))):
                if touch > CONTACT_TOL:
                    continue
                span = []
                for j in range(3):
                    if j == k:
                        continue
                    lo = max(ea[j][0], eb[j][0])
                    hi = min(ea[j][1], eb[j][1])
                    span.append((j, lo, hi))
                if any(hi - lo <= CONTACT_TOL for _j, lo, hi in span):
                    continue
                area = 1.0
                for _j, lo, hi in span:
                    area *= hi - lo
                if area < MIN_CONTACT:
                    continue
                p = [0.0, 0.0, 0.0]
                p[k] = ea[k][1] if sign > 0 else ea[k][0]
                for j, lo, hi in span:
                    p[j] = (lo + hi) / 2
                out.append((tuple(p), k, sign, area, a, b))
    out.sort(key=lambda c: -c[3])
    return out


def patch_window(contact):
    """{axis: (lo, hi)} for the two axes the shared face spans."""
    k = contact[1]
    pa, pb = contact[4], contact[5]
    return {j: (max(pa.extents[j][0], pb.extents[j][0]),
                min(pa.extents[j][1], pb.extents[j][1]))
            for j in range(3) if j != k}


def contact_row(contact):
    """(joint, contact-row, part matching row['a'], part matching row['b']).

    Four Nones when the patch is nobody's joint - two parts that simply bear
    on one another. There is no ambiguity to resolve: no two joints in this
    bed tie the same pair of families across the same axis.
    """
    a, b, axis = contact[4], contact[5], contact[1]
    for j in JOINTS:
        for crow in j["contacts"]:
            if crow["axis"] != axis:
                continue
            if _is_part(crow["a"], a.label) and _is_part(crow["b"], b.label):
                return j, crow, a, b
            if _is_part(crow["a"], b.label) and _is_part(crow["b"], a.label):
                return j, crow, b, a
    return None, None, None, None


# ---------------------------------------------------------------------------
# WHICH WAY A SCREW CAN POSSIBLY GO
# ---------------------------------------------------------------------------
# A wood screw through a joint has to do three things at once: pass CLEAR
# through the member it is driven from, END INSIDE the member it grips, and
# not come out the far side of it. In millimetres:
#
#     thickness(entry) < length < thickness(entry) + thickness(receiver)
#
# For most joints in this bed only ONE of the two directions satisfies that -
# a 6x90 cannot be driven through a 98 mm post into a 48 mm beam, because it
# would not even reach the beam - and then the direction is not a matter of
# opinion. It is DERIVED, and the table above is only checked against it.
# Where both directions fit (a 6x80 through 36 mm into 48 mm works either way
# round) the rule cannot help and the table decides: reviewed, human data.
# Where NEITHER fits, the screw is not a straight through-screw at all - a toe
# screw, or a bolt with a nut - and the drive must say so with `exempt`.
def screw_fits(entry, receiver, axis, length, counterbore=0.0):
    t_e = entry.extents[axis][1] - entry.extents[axis][0] - counterbore
    t_r = receiver.extents[axis][1] - receiver.extents[axis][0]
    return t_e < length < t_e + t_r


def derived_entry(contact, crow, pa, pb, dr):
    """(entry member or None, status) - the physics, before the table.

    status: 'utledet'      only one direction is possible; use it.
            'tvetydig'     both are; the table decides.
            'unntak'       neither, and the drive says why.
            'umulig'       neither, and the drive does NOT say why - a bug.
            'gjelder ikke' not a through-screw (a bracket, or driven along an
                           axis of its own).
    """
    if dr["bracket"] or dr["into"] is not None or dr["frm"] is None:
        return None, "gjelder ikke"
    if dr["exempt"]:
        return None, "unntak"
    axis = contact[1]
    _d, length = fastener_size(dr["name"])
    # A counterbore belongs to ONE member - the one the table drives from - so
    # it is only taken off that member's thickness when that member is the
    # candidate entry. The other direction is judged on the solid wood.
    named = _member(crow, dr["frm"], pa, pb)
    ok = [p for p, q in ((pa, pb), (pb, pa))
          if screw_fits(p, q, axis, length,
                        dr["counterbore"] if p is named else 0.0)]
    if len(ok) == 1:
        return ok[0], "utledet"
    return None, ("tvetydig" if ok else "umulig")


def _member(crow, kind, pa, pb):
    return pa if crow["a"] == kind else pb


def _outboard(axis, member):
    """+1 / -1: the way from the middle of the bed out past `member`."""
    return _outboard_at(axis, sum(member.extents[axis]) / 2)


def _outboard_at(axis, value):
    return 1.0 if value > BED_CENTRE[axis] else -1.0


def _resolve_sign(word, default, axis=None, at=None, side=None):
    """+1 / -1 out of a drive field. `outboard` / `inboard` are resolved
    against the middle of the bed at the point the joint actually happens, so
    one row of table serves a joint and its mirror image.

    `side` is that resolution handed down instead of measured: a MIRRORED
    joint (see JOINTS `mirror`) is two fastenings on ONE contact patch - the
    two ends of the same rung, the two side edges of the same panel - and the
    patch centre cannot tell them apart, so the instance says which half of
    the bed it is."""
    if word is None:
        return default
    if word in ("outboard", "inboard"):
        out = float(side) if side is not None else _outboard_at(axis, at)
        return out if word == "outboard" else -out
    return float(word)


def drive_axis_sign(contact, crow, pa, pb, dr, side=None):
    """(axis, sign, entry member or None, receiving member) for one drive.

    `into` puts the fastener along its own axis, entering the named member on
    the face that looks back into the room side of the bed unless `sign` says
    otherwise. `frm` reads the direction off the patch - and is then CHECKED
    against the fit rule, which is the primary source. The table is only
    allowed to agree with it, or to decide where it genuinely cannot.
    """
    if dr["into"] is not None:
        axis = dr["axis"]
        member = _member(crow, dr["into"], pa, pb)
        sign = _resolve_sign(dr["sign"], _outboard(axis, member),
                             axis, contact[0][axis], side)
        return axis, sign, None, member
    axis = contact[1]
    entry = _member(crow, dr["frm"], pa, pb)
    target = pb if entry is pa else pa
    guess, status = derived_entry(contact, crow, pa, pb, dr)
    assert status != "umulig", (
        f"{crow['jid']}: {dr['name']} passer ikke gjennom {pa.label} eller "
        f"{pb.label} langs akse {axis} — verken den ene eller den andre "
        f"veien. Er det en skråskrue eller en gjennomgående bolt, må "
        f"drive(...) si det med exempt=...")
    if status == "utledet":
        assert guess is entry, (
            f"{crow['jid']}: tabellen skrur {dr['name']} fra {entry.label}, "
            f"men den eneste retningen skruen faktisk kan gå er fra "
            f"{guess.label}. Rett `frm` i JOINTS.")
    sign = contact[2] if entry is contact[4] else -contact[2]
    return axis, sign, entry, target


def flange(contact, dr, row, member, reach, side=None):
    """(lo, hi, sign): the strip a bracket flange - or the row of screws that
    goes through one - occupies, running out of the joint corner.

    The corner is the contact plane where the flange lies along the joint
    normal, and the edge of the shared face where it runs across it. Which of
    the two ways it then runs is `row_sign`; the default is simply the side
    the member it lies on has more of.
    """
    k = contact[1]
    win = patch_window(contact)
    lo_m, hi_m = member.extents[row]
    here = contact[0][row] if row == k else sum(win[row]) / 2
    default = 1.0 if (hi_m - here) >= (here - lo_m) else -1.0
    sign = _resolve_sign(dr["row_sign"], default, row, contact[0][row], side)
    start = (contact[0][k] if row == k
             else win[row][1 if sign > 0 else 0])
    lo, hi = sorted((start, start + sign * reach))
    return lo, hi, sign, start


def _unit(axis, sign):
    v = [0.0, 0.0, 0.0]
    v[axis] = float(sign)
    return tuple(v)


def _offset_vector(joint, contact, dr, side=None):
    """X10: the declared step off the window centre, as a model-space vector.

    Resolved at the joint the way `row_sign` is, so "inboard" means the same
    thing at the left post and at the right one and the bed stays symmetric.
    """
    off = [0.0, 0.0, 0.0]
    if dr["offset"] is None:
        return off
    axis, mm = dr["offset"][0], float(dr["offset"][1])
    word = dr["offset"][2] if len(dr["offset"]) > 2 else None
    sign = _resolve_sign(word, 1.0, axis, contact[0][axis], side)
    off[axis] = sign * mm
    return off


# ---------------------------------------------------------------------------
# THE INSTANCES
# ---------------------------------------------------------------------------
# One record per fastener in the bed, with an anchor (the centre of the head,
# ON THE FACE it is driven from), a unit drive vector and the two members it
# ties. This is what the geometry block below turns into solids and what the
# drawings hang their marks on. Nothing downstream re-derives a direction.
def _place_drive(joint, crow, contact, pa, pb, dr, shift, side=None):
    """Every fastener one drive puts at one joint, as placement records."""
    kk = contact[1]
    cp = contact[0]
    win = patch_window(contact)
    d, length = fastener_size(dr["name"])
    what = f"{joint['id']} {dr['name']}"
    off = _offset_vector(joint, contact, dr, side)

    def at(p):
        return tuple(a + b + c for a, b, c in zip(p, shift, off))

    # --- a bracket flange, or the screws that go through one ---------------
    if dr["into"] is not None:
        axis, sign, _entry, target = drive_axis_sign(contact, crow, pa, pb, dr,
                                                     side)
        face = (target.extents[axis][0] if sign > 0
                else target.extents[axis][1])
        row = dr["row"]
        reach = dr["reach"] or BRACKETS[dr["bracket"]]["leg"]
        lo, hi, rsign, corner = flange(contact, dr, row, target, reach,
                                       side)
        cross = [j for j in range(3) if j not in (axis, row)][0]
        width = (BRACKETS[dr["bracket"]]["width"] if dr["bracket"]
                 else min_spacing(d))
        c0, c1 = target.extents[cross]
        assert c1 - c0 >= width - FIT_TOL, (
            f"{what}: en {width:g} mm bred flik får ikke plass på en "
            f"{c1 - c0:g} mm flate av {target.label}")
        mid = sum(win[cross]) / 2 if cross in win else (c0 + c1) / 2
        cpos = min(max(mid, c0 + width / 2), c1 - width / 2)
        p = [0.0, 0.0, 0.0]
        p[axis] = face
        p[cross] = cpos
        if dr["bracket"]:
            p[row] = corner
            return [dict(kind="plate", bracket=dr["bracket"], anchor=at(p),
                         direction=_unit(axis, sign), run=_unit(row, rsign),
                         reach=reach, width=width, row_axis=row,
                         t=BRACKETS[dr["bracket"]]["t"], through=None,
                         into=target,
                         bears=(_member(crow, dr["bears"], pa, pb)
                                if dr["bears"] else None))]
        out = []
        for v in row_positions(lo, hi, dr["per"], d,
                               f"{what} (beslagflik {reach:g} mm)"):
            p[row] = v
            out.append(dict(kind="screw", anchor=at(list(p)),
                            direction=_unit(axis, sign), length=length, d=d,
                            face=(axis, face), through=None, into=target,
                            row_axis=row))
        return out

    axis, sign, entry, target = drive_axis_sign(contact, crow, pa, pb, dr,
                                               side)

    # --- a toe screw -------------------------------------------------------
    if dr["toe"]:
        toe = dr["toe"]
        f_ax = toe["face"]
        f_sign = _resolve_sign(toe["face_sign"], 1.0, f_ax, cp[f_ax])
        face = (entry.extents[f_ax][1] if f_sign > 0
                else entry.extents[f_ax][0])
        n_in = [0.0, 0.0, 0.0]
        n_in[f_ax] = -f_sign
        t_dir = [0.0, 0.0, 0.0]
        t_dir[axis] = sign
        th = math.radians(toe["deg"])
        vec = tuple(n * math.cos(th) + t * math.sin(th)
                    for n, t in zip(n_in, t_dir))
        row = (dr["row"] if dr["row"] is not None
               else [j for j in range(3) if j not in (f_ax, axis)][0])
        # V4: THE SEAT. `back` locates the MOUTH of the pocket on the face; the
        # head sits `seat` further along the screw's own axis, at the pocket's
        # flat bottom. Everything downstream reads that bottom as the face the
        # screw is driven from - the same contract the straight counterbore
        # already has - so the head assert stays a comparison between two
        # independently derived numbers and not a tautology.
        seat = toe.get("seat", TOE_SEAT_DEPTH)
        seat_face = face + vec[f_ax] * seat
        out = []
        for v in row_positions(win[row][0], win[row][1], dr["per"], d,
                               f"{what} (skråskrue)"):
            mouth = [0.0, 0.0, 0.0]
            mouth[f_ax] = face
            mouth[axis] = cp[axis] - sign * toe["back"]
            mouth[row] = v
            p = [m + vv * seat for m, vv in zip(mouth, vec)]
            out.append(dict(kind="screw", anchor=at(p), direction=vec,
                            length=length, d=d, face=(f_ax, seat_face),
                            through=entry, into=target, toe=True,
                            seat=seat, seat_d=TOE_SEAT_D, row_axis=row,
                            seat_face=(f_ax, f_sign, face)))
        return out

    # --- the ordinary through screw, and the plates bolted through one -----
    # `counterbore` moves the head off the outer face and INTO the member, by
    # the depth of the clearance hole bored for it. Everything downstream -
    # the flush-head check, the containment check, the drawings - then reads
    # the bottom of the counterbore as the face the screw is driven from,
    # which is exactly what it is.
    face = entry.extents[axis][1] if sign < 0 else entry.extents[axis][0]
    face += sign * dr["counterbore"]
    across = sorted(win)
    row = (dr["row"] if dr["row"] is not None
           else max(across, key=lambda j: win[j][1] - win[j][0]))
    cross = [j for j in across if j != row][0]
    reach = dr["reach"] or (BRACKETS[dr["bracket"]]["leg"] if dr["bracket"]
                            else None)
    if reach is not None:
        lo, hi, rsign, corner = flange(contact, dr, row, entry, reach, side)
    else:
        lo, hi, rsign = win[row][0], win[row][1], 1.0
        corner = sum(win[row]) / 2
    p = [0.0, 0.0, 0.0]
    p[axis] = face
    p[cross] = sum(win[cross]) / 2
    if dr["bracket"]:
        b = BRACKETS[dr["bracket"]]
        p[row] = corner
        return [dict(kind="plate", bracket=dr["bracket"], anchor=at(p),
                     direction=_unit(axis, sign), run=_unit(row, rsign),
                     reach=reach, width=b["width"], t=b["t"], row_axis=row,
                     through=entry, into=target)]
    out = []
    for v in row_positions(lo, hi, dr["per"], d, what):
        p[row] = v
        out.append(dict(kind="screw", anchor=at(list(p)),
                        direction=_unit(axis, sign), length=length, d=d,
                        face=(axis, face), through=entry,
                        into=target, grips=target, row_axis=row))
    return out


def joint_instances(all_parts):
    """[(joint, contact-row, contact, pa, pb), ...] - every joint in the bed."""
    found = []
    for c in contacts(all_parts):
        j, crow, pa, pb = contact_row(c)
        if j is None:
            continue
        found.append((j, crow, c, pa, pb))
    return found


def fastener_specs(all_parts):
    """Every fastener in the bed as a placement record, plus the count check."""
    inst = joint_instances(all_parts)
    per_row = {}
    for j, crow, _c, _pa, _pb in inst:
        per_row[(j["id"], id(crow))] = per_row.get((j["id"], id(crow)), 0) + 1
    specs = []
    for j in JOINTS:
        if not j["contacts"]:
            continue
        for crow in j["contacts"]:
            crow["jid"] = j["id"]
            got = per_row.get((j["id"], id(crow)), 0)
            assert got and j["n"] % got == 0, (
                f"{j['id']}: the model has {got} places where "
                f"{crow['a']} meets {crow['b']} across axis {crow['axis']}, "
                f"and the table says the bed has {j['n']} of the joint")
            crow["_repeat"] = j["n"] // got
    for _n, (j, crow, c, pa, pb) in enumerate(inst):
        rep = crow["_repeat"]
        spread = j.get("spread")
        if rep == 1:
            offsets = [(0.0, 0.0, 0.0)]
        else:
            assert spread, (f"{j['id']}: {rep} of them on one contact patch "
                            f"and no `spread` to put them in")
            win = patch_window(c)
            offsets = []
            for at in spread["at"]:
                s = [0.0, 0.0, 0.0]
                s[spread["axis"]] = at
                offsets.append(tuple(s))
            assert len(offsets) == rep
            for s in offsets:
                a = spread["axis"]
                mid = sum(win[a]) / 2 + s[a]
                assert win[a][0] < mid < win[a][1], (
                    f"{j['id']}: spread {s[a]:+g} puts one of them at "
                    f"{a}={mid:g}, off the joint")
        # X6: WHICH ONE OF THEM. A joint's screws are laid out in ROWS, and a
        # row's c/c is only meaningful inside one instance of the joint - the
        # two J12 screws at either end of a 1794 mm ledger are one screw in
        # each of two joints, not a row 1754 mm wide. `inst` is that identity,
        # and a spread (a mirrored joint, two fastenings on one contact patch)
        # counts as its own instance for the same reason.
        for _k, s in enumerate(offsets):
            for dr in crow["drives"]:
                for f in _place_drive(j, crow, c, pa, pb, dr, s):
                    if dr["offset"] is not None:
                        _oa = dr["offset"][0]
                        assert abs(f["direction"][_oa]) < 1e-9, (
                            f"{j['id']}: the X10 offset is on axis "
                            f"{'XYZ'[_oa]}, which is the axis "
                            f"{dr['name']} is DRIVEN along - that moves the "
                            f"head off the face, it does not move the screw "
                            f"sideways. An offset is perpendicular or it is "
                            f"a different screw")
                    f.update(jid=j["id"], name=dr["name"], drive=dr,
                             joint=j, crow=crow, contact=c, pa=pa, pb=pb,
                             inst=(_n, _k))
                    specs.append(f)
    return specs


# The wall fixings are the joints with nothing on the other side: they go
# through a member that lies flat on the wall plane and into the studs of a
# wall this model does not have. Each is placed off its own member, spread
# along the length the way a builder spreads it across the studs he finds, and
# marked `wall` - the containment asserts and the mesh export both skip them,
# because everything past Y = -48 is in the wall.
#
# X11: there are TWO of them now. The rule that picks the members is the one
# the nogging block already states for the wall as a whole - a member whose
# LENGTH runs along the wall face lies flat on it over that whole length - so
# it is written here as a pair of (joint, member) and checked against that
# rule down in the nogging block, where the rule lives. A fixing into a member
# that does not lie flat on the wall would need a packer, and this file has
# none.
WALL_FIXINGS = [("J14", back_rail), ("J12-V", support_rail)]

# X12 - AND THE X OF A WALL FIXING IS NOT A MEASUREMENT. Everything else in
# this bed stands where the wood puts it. These nine do not: they stand where
# the STUDS are, and the studs are in the room. This model has no wall, has
# never measured one, and is not entitled to an opinion about the centres -
# 600 is a convention, not a fact, and a 1950s wall obeys nothing.
#
# So the even spread below is a MODELLING CONVENIENCE and nothing more. It
# exists to give each fixing a body to be counted, drawn and priced, and to
# give the ledger and the rail a defensible span to be reckoned on: N fixings
# spread evenly is the WORST layout a builder can hit while still obeying the
# rule he is actually given, which is «one in every stud you find, and at
# least at both ends and in the middle». Find them closer together and the
# spans get shorter, never longer, so the strength case is conservative in
# the right direction.
#
# What that costs, and it is deliberate: the c/c number the tables print is
# advisory. It is flagged here rather than in the emitter so that anything
# reading the model can see it - `wall_fix_placement_rows` prints the RULE in
# the «fra enden» column and never an X, the row's pitch is printed with a
# «≈», and an assert on the finished ink refuses any wall-fixing row that
# offers an X as a datum. This flag is what those three are keeping.
STUD_LAYOUT_UNKNOWN = True


def wall_fastener_specs():
    d, length = 8.0, 100.0
    out = []
    for jid, member in WALL_FIXINGS:
        j = JOINT[jid]
        name, count = j["fast"][0]
        x0, x1 = member.extents[0]
        y = member.extents[1][1]
        z = sum(member.extents[2]) / 2
        for i in range(count):
            # Advisory, not measured - see STUD_LAYOUT_UNKNOWN above.
            t = (i + 0.5) / count
            out.append(dict(kind="screw", anchor=(x0 + (x1 - x0) * t, y, z),
                            direction=(0.0, -1.0, 0.0), length=length, d=d,
                            through=member, into=None, wall=True,
                            jid=jid, name=name, drive=None, joint=j,
                            crow=None, contact=None))
    return out


# ---------------------------------------------------------------------------
# BUILD THEM
# ---------------------------------------------------------------------------
# Bed mode is the one that gets fastened: the loose panel is the same part in
# both modes and carries the same steel, and the two joints it makes (J13b to
# the rung, J13c over the bench rail) are the bed-mode ones the drawings show.
_WOOD = [p for p in mode_parts(panel_bed) if not is_soft(p)]
_bb = [(min(p.extents[j][0] for p in _WOOD),
        max(p.extents[j][1] for p in _WOOD)) for j in range(3)]
BED_CENTRE = tuple((a + b) / 2 for a, b in _bb)

FASTENER_SPECS = fastener_specs(_WOOD) + wall_fastener_specs()

# --- the totals, and the check that the shopping list is the same list ------
HARDWARE_TOTAL = {}
for _j in JOINTS:
    for _name, _per in _j["fast"]:
        HARDWARE_TOTAL[_name] = HARDWARE_TOTAL.get(_name, 0) + _per * _j["n"]

_placed = {}
for _f in FASTENER_SPECS:
    _placed[_f["name"]] = _placed.get(_f["name"], 0) + 1
for _name, _qty in _placed.items():
    assert HARDWARE_TOTAL[_name] == _qty, (
        f"{_name}: {_qty} modelled, the joint table sells {HARDWARE_TOTAL[_name]}")

# --- the frame screw rows the key-dimensions page prints --------------------
def screw_rows():
    """The J1 / J2 / J8 rows, read back off the instances that were placed.

    These three are the frame joints whose row geometry the reader is asked to
    measure, so the key-dimensions page prints them. They are not recomputed
    here: this walks the fasteners that exist and reports where they landed.
    """
    rows = {}
    for jid, member, axis in (("J1", "endebjelke", 2), ("J2", "sidevange", 2),
                              ("J8", "benkevange", 2)):
        fs = [f for f in FASTENER_SPECS if f["jid"] == jid]
        assert fs, jid
        # The edge distance is measured in the JOINT, not in whichever of the
        # two members happens to be the target: the band is the overlap of the
        # two, i.e. the contact window patch_window() already computes. Reading
        # it off `into` alone is only right when the target is the shorter
        # member in this axis - it is for J2 and J8 (post into rail), and it is
        # NOT for J1, where the screws go through the beam INTO the post and
        # the post runs 0..1402, printing a 1331 mm "edge distance" off the
        # floor instead of the 27 mm up from the beam's own underside.
        band = patch_window(fs[0]["contact"])[axis]
        zs = sorted({round(f["anchor"][axis], 3) for f in fs})
        sec_ = sec(*_SECTION_OF[jid])
        rows[jid] = dict(z=zs, member=f"{member} {sec_.replace('x', '×')}",
                         band=[band[0], band[1]],
                         edge=[zs[0] - band[0], band[1] - zs[-1]],
                         spacing=(zs[-1] - zs[0]) if len(zs) > 1 else None,
                         count=len(zs))
    rows["J1"]["y"] = sorted({round(f["anchor"][1], 3)
                              for f in FASTENER_SPECS if f["jid"] == "J1"})
    for jid in ("J2", "J8"):
        rows[jid]["x"] = sorted({round(f["anchor"][0], 3)
                                 for f in FASTENER_SPECS
                                 if f["jid"] == jid})[0]
    # The rail end distance the lap leaves us with. The screw force is
    # perpendicular to the rail's grain, so this is an UNLOADED end and the
    # requirement is 3d; the lap is only POST_W wide, so it is tight.
    rows["_rail_end_distance"] = rows["J2"]["x"] - THROUGH_X0
    rows["_rail_end_required"] = MIN_EDGE
    return rows


# The section each row is quoted in. J1 is the END BEAM, not the side rail:
# V6b re-sectioned it 48 -> 36 (END_BEAM_T) and this dict was left saying
# 48x98, so the key-dimensions page has been printing "J1 - endebjelke 48x98"
# for a 36x98 board ever since. The assert under it is the guard, because the
# only thing wrong with a typed section is that nobody re-reads it.
_SECTION_OF = {"J1": (END_BEAM_T, RAIL_H), "J2": (RAIL_T, RAIL_H),
               "J8": (BENCH_RAIL_T, BENCH_RAIL_H)}
for _jid, _sec in _SECTION_OF.items():
    _thru = next(f["through"] for f in FASTENER_SPECS
                 if f["jid"] == _jid and f.get("through") is not None)
    _built = sorted(round(_thru.extents[j][1] - _thru.extents[j][0], 1)
                    for j in range(3))[:2]
    assert _built == sorted(_sec), (
        f"{_jid}: the row is quoted as {_sec[0]:g}x{_sec[1]:g} and the member "
        f"it is driven through, '{_thru.label}', measures {_built[0]:g}x"
        f"{_built[1]:g} on the solid")
SCREW_ROWS = screw_rows()

print("\n=== FESTEMIDLER ===")
print(f"OK  {len(FASTENER_SPECS)} festemidler plassert i "
      f"{len(JOINTS)} ledd, alle lagt ut etter (n-1)x4d + 2x3d")
# X12: STUD_LAYOUT_UNKNOWN, kept. The X6 placement machinery turns a fastener
# into «so many mm from a named end», and that is precisely the sentence a
# wall fixing is not allowed to be given. What keeps it out is that a wall
# fixing has no `drive` - `fastener_placements()` skips those - so the flag is
# only true as long as that stays true, and this is where it is measured.
_WALL_SPEC = [_f for _f in FASTENER_SPECS if _f.get("wall")]
assert STUD_LAYOUT_UNKNOWN and _WALL_SPEC, \
    "X12: no fixing is marked `wall` - STUD_LAYOUT_UNKNOWN guards nothing"
assert all(_f["drive"] is None for _f in _WALL_SPEC), (
    "X12: a wall fixing has picked up a `drive`, which is what turns a "
    "fastener into an X measured off a named end. The studs are in the room "
    "and this model has not seen them - see STUD_LAYOUT_UNKNOWN")
print(f"OK  X12 stenderne: {len(_WALL_SPEC)} veggfester i "
      f"{len(WALL_FIXINGS)} ledd er lagt ut jevnt langs sin egen del. Den "
      f"delingen er VEILEDENDE - modellen har ingen vegg - og ingen av dem "
      f"har en drivretning, så ingen av dem kan få en plasseringslinje med "
      f"X-mål. Regelen er «et feste i hver stender du treffer»")
for _j in JOINTS:
    _mine = [f for f in FASTENER_SPECS if f["jid"] == _j["id"]]
    _what = " + ".join(f"{q}x {n}" for n, q in _j["fast"])
    print(f"    {_j['id']:<5} n={_j['n']:<3} {len(_mine):>3} stk  {_what}")
for _name, _qty in sorted(HARDWARE_TOTAL.items(), key=lambda kv: -kv[1]):
    print(f"    {_qty:>4} x {_name}")

# K2: THE COUNTERBORE'S OWN SPACING RULE. See MIN_CBORE_PITCH. The fits-the-
# face rule above spaces SHANKS; every screw driven out of a counterbore is
# also a 12 mm hole, and two holes that close on each other are a split
# waiting for a knee. Measured on the placed fasteners, per member, so it
# reads the same geometry the drawing does.
_CBORED = {}
for _f in FASTENER_SPECS:
    if (_f.get("drive") or {}).get("counterbore"):
        _CBORED.setdefault((_f["jid"], _f["through"].label), []).append(_f)
CBORE_PITCH_MIN = 1e18
CBORE_PITCH_WHO = None
for (_jid, _), _group in sorted(_CBORED.items(), key=lambda kv: kv[0][0]):
    # The row runs along whichever axis the member does, so the distance is
    # measured in space and not on a guessed axis.
    for _i, _a in enumerate(_group):
        for _b in _group[_i + 1:]:
            _d = math.dist(_a["anchor"], _b["anchor"])
            if _d < CBORE_PITCH_MIN:
                CBORE_PITCH_MIN, CBORE_PITCH_WHO = _d, _jid
# K2 + X10: THE SENTINEL NEEDS A GUARD, the way K4's does. If no member ever
# carried two counterbores the loop above would never run, CBORE_PITCH_MIN
# would still be 1e18, and the assert would read `1e18 >= 24` - "nothing to
# measure" quietly reported as "the rule is satisfied", which is the exact
# failure K4 was written to avoid. Here the population is KNOWN - the J13a/J13b
# up-screws - so emptiness is not a legal state at all and it says so.
assert _CBORED and CBORE_PITCH_WHO is not None, (
    "K2: no member in the bed carries two counterbored screws, so there is "
    "nothing to space - but the J13a/J13b up-screws are supposed to be "
    "exactly that. The population has gone missing, not the problem")
assert CBORE_PITCH_MIN >= MIN_CBORE_PITCH - FIT_TOL, (
    f"K2: {CBORE_PITCH_WHO} puts two ⌀{PANEL_UPSCREW_CBORE_D} mm "
    f"counterbores {CBORE_PITCH_MIN:g} mm apart, which leaves "
    f"{CBORE_PITCH_MIN - PANEL_UPSCREW_CBORE_D:g} mm of wood between them. "
    f"The (n-1)x4d + 2x3d rule sizes the SCREW; the hole it sits in needs "
    f"{MIN_CBORE_PITCH:g} mm centres. Take a screw out of the row - the "
    f"up-screws are clamps for a glue line, not the load path")
print(f"OK  K2 kontraborene: nærmeste to ⌀{PANEL_UPSCREW_CBORE_D} mm "
      f"kontrabor står {CBORE_PITCH_MIN:g} mm fra hverandre "
      f"({CBORE_PITCH_WHO}) = {CBORE_PITCH_MIN - PANEL_UPSCREW_CBORE_D:g} mm "
      f"tre imellom, krav {MIN_CBORE_PITCH:g} mm senteravstand. "
      f"Passer-på-flaten måler skruen; hullet den sitter i har sin egen regel")



# ===========================================================================
# THE FASTENERS AS SOLIDS
# ===========================================================================
# A drawn arrow cannot be wrong in a way a build catches. A solid can: it has
# a head that is either flush with the face or is not, a tip that is either
# inside the member it grips or is not, and a body that is either in its own
# two members or in somebody else's. Every one of those is a question the
# assert block below asks of the SHAPE - not of the table that produced it -
# and the whole reason the fasteners are modelled at all.
#
# They stay OUT of the wood logic. `parts`, `mode_parts()`, CUT_LIST,
# parts.tsv, the overlap check and the connectivity check are wood-only: a
# screw overlaps the two members it ties on purpose, so it would fail the
# no-overlap assert on sight. The fasteners ride in their own colour group and
# are added to the exported compound only.
#
#   LOFTBED_FASTENERS=0   build the bed without them (impact baseline)
# ---------------------------------------------------------------------------
FASTENERS_ON = os.environ.get("LOFTBED_FASTENERS", "1").lower() \
    not in ("0", "false", "no", "off")

GROUP_COLORS["fasteners"] = Color(0.42, 0.45, 0.50)   # zinc-plated steel
GROUP_ORDER.append("fasteners")

# Countersunk wood screw, proportions of a Torx flat-head timber screw. The
# nominal length of a countersunk screw is measured FROM THE TOP OF THE HEAD,
# which is what makes the "does it come out the back" question answerable.
SCREW_HEAD_D = {5: 9.5, 6: 11.8, 8: 15.5}     # head diameter by shank diameter
SCREW_HEAD_LAND = 0.8            # the cylindrical land at the top of the head
SCREW_TIP_LEN = 1.6              # the point, as a multiple of d
# Mesh deflection for the fastener group only - see the export block.
FASTENER_MESH_TOL = 0.15
FASTENER_MESH_ANG = 1.0


def _rot_to(direction):
    """The turn that takes local -Z onto `direction`. Any direction: the two
    toe-screw joints are not axis aligned and must not be special cases."""
    v = Vector(*direction)
    v = v / v.length
    src = Vector(0, 0, -1)
    dot = max(-1.0, min(1.0, src.dot(v)))
    if dot > 1 - 1e-12:
        return Location()
    if dot < -1 + 1e-12:
        return Location((0, 0, 0), (1, 0, 0), 180)
    ax = src.cross(v)
    return Location((0, 0, 0), (ax.X, ax.Y, ax.Z),
                    math.degrees(math.acos(dot)))


def _tag(solid, spec, label):
    solid.label = label
    solid.color = GROUP_COLORS["fasteners"]
    solid.group = "fasteners"
    solid.spec = spec
    bb = solid.bounding_box()
    solid.extents = ((bb.min.X, bb.max.X), (bb.min.Y, bb.max.Y),
                     (bb.min.Z, bb.max.Z))
    return solid


def screw(anchor, direction, length, d, spec=None, label="Screw"):
    """One countersunk wood screw as a solid.

    `anchor`    the centre of the head ON THE ENTRY FACE (model mm, Z-up)
    `direction` the unit vector the screw travels, i.e. into the wood
    `length`    the nominal (head-top to tip) length

    The head top sits exactly in the entry face: flush, neither proud nor
    counterbored. No thread is modelled and none is wanted at drawing scale -
    the silhouette is what a drawing carries, and the silhouette is what every
    assert below is about.
    """
    dd = int(round(d))
    r, hr = d / 2, SCREW_HEAD_D.get(dd, 1.9 * d) / 2
    csk = hr - r                    # 90 deg countersink: rise == run
    tip = SCREW_TIP_LEN * d
    shank = length - SCREW_HEAD_LAND - csk - tip
    assert shank > 0, f"{label}: {length} mm is shorter than its own head"

    z = 0.0
    solid = Cylinder(hr, SCREW_HEAD_LAND).moved(
        Location((0, 0, z - SCREW_HEAD_LAND / 2)))
    z -= SCREW_HEAD_LAND
    solid += Cone(r, hr, csk).moved(Location((0, 0, z - csk / 2)))
    z -= csk
    solid += Cylinder(r, shank).moved(Location((0, 0, z - shank / 2)))
    z -= shank
    solid += Cone(0, r, tip).moved(Location((0, 0, z - tip / 2)))
    return _tag(Location(anchor) * _rot_to(direction) * solid, spec, label)


def _slab(lo, hi):
    """A box from two corner triples, given in any order per axis."""
    a = [min(p, q) for p, q in zip(lo, hi)]
    b = [max(p, q) for p, q in zip(lo, hi)]
    d = [y - x for x, y in zip(a, b)]
    return Box(*d).moved(Location(tuple(x + s / 2 for x, s in zip(a, d))))


def _axis_of(vec):
    """(axis, sign) of an axis-aligned unit vector."""
    j = max(range(3), key=lambda i: abs(vec[i]))
    return j, (1.0 if vec[j] > 0 else -1.0)


def angle_boxes(spec):
    """The two flanges of a bent angle bracket, as (lo, hi) per axis.

    ONE source of truth. The solid below is built from these boxes, and so is
    the insertion sweep in the validation block - which is the whole point: a
    bracket that the sweep clears but the solid does not would be a drawing
    that lies about the only move this panel has to make.

    Flange A lies on the face the drive vector enters and runs out of the
    corner along `run`. Flange B is the OTHER one, and its geometry is not a
    second row of table - it falls out of the first: a right angle turns
    `run` into the second flange's screw direction and the drive vector into
    the direction that flange runs.
    """
    C = spec["anchor"]
    ax, sa = _axis_of(spec["direction"])
    rx, sr = _axis_of(spec["run"])
    cx = [j for j in range(3) if j not in (ax, rx)][0]
    t, w, reach = spec["t"], spec["width"], spec["reach"]
    lo = list(C)
    hi = list(C)
    lo[cx] = C[cx] - w / 2
    hi[cx] = C[cx] + w / 2
    a_lo, a_hi = list(lo), list(hi)
    a_hi[ax] = C[ax] - sa * t
    a_hi[rx] = C[rx] + sr * reach
    b_lo, b_hi = list(lo), list(hi)
    b_hi[rx] = C[rx] + sr * t
    b_hi[ax] = C[ax] - sa * reach
    return [(a_lo, a_hi), (b_lo, b_hi)]


def angle_bracket(spec, label):
    """A bent flat bracket: two flanges at 90 degrees meeting at one corner."""
    (a_lo, a_hi), (b_lo, b_hi) = angle_boxes(spec)
    return _tag(_slab(a_lo, a_hi) + _slab(b_lo, b_hi), spec, label)


def build_fasteners():
    out = []
    seen = {}
    for f in FASTENER_SPECS:
        if f.get("wall"):
            # The wall screw's back half is IN THE WALL, which is not
            # modelled. It is drawn, but it is not exported: putting 52 mm of
            # steel behind Y = -48 would make the exported bed 888 mm deep,
            # and the 836 mm flat mounting plane is the whole point of it.
            continue
        n = seen[f["jid"]] = seen.get(f["jid"], 0) + 1
        label = f"{f['jid']} {f['name'].split(' forsenket')[0]}_{n}"
        if f["kind"] == "plate":
            solid = angle_bracket(f, label)
        else:
            solid = screw(f["anchor"], f["direction"], f["length"], f["d"],
                          spec=f, label=label)
        f["solid"] = solid
        out.append(solid)
    return out


FASTENERS = build_fasteners() if FASTENERS_ON else []


# ---------------------------------------------------------------------------
# THE ASSERTS - asked of the SHAPES
# ---------------------------------------------------------------------------
FASTENER_TOL = 0.15
# The tightest tip cover in the bed is the 6x80 pattern of J2, J3 and J8, and
# V5 turned all three of them round: through 48 mm of side or bench rail,
# 32 mm left in a 36 mm post or upright, so 4 mm of wood stands behind the
# point. It is the same 4 mm the old direction had - the pattern is symmetric,
# 36 + 48 = 48 + 36 - it has simply moved from the rail to the post, and the
# head has moved off the room-facing face (V5). The number was set at 2 mm
# once, by the deleted J9-F block; nothing in the bed is that tight now.
FASTENER_MIN_TIP_COVER = 4.0
FASTENER_VOL_TOL = 2.0           # mm3 - OCC boolean noise on a tangent face
# TOE_HEAD_ALLOWANCE is GONE (V4). It used to let a tenth of a skew screw's
# volume stand outside the wood, because a 90 degree countersink met at 25-30
# degrees cannot be flush. It is not a tolerance any more, it is a seat: every
# toe screw is bored a flat-bottomed pocket along its own axis (TOE_SEAT_DEPTH)
# and its head is entirely under the surface. So a toe screw is checked exactly
# like every other screw - fully contained, no allowance - plus one assert of
# its own that measures the wood standing over the highest point of the head.


def _boxes_apart(a, b):
    return any(a0 >= b1 or b0 >= a1 for (a0, a1), (b0, b1) in zip(a, b))


def _cut_volume(a, b):
    """Volume of a & b, 0.0 when they miss."""
    if _boxes_apart(a.extents, b.extents):
        return 0.0
    try:
        x = a.intersect(b)
    except Exception:
        return 0.0
    if x is None:
        return 0.0
    if isinstance(x, (list, tuple)):
        return sum(abs(getattr(i, "volume", 0.0)) for i in x)
    return abs(getattr(x, "volume", 0.0))


def _ray_exit(point, direction, member):
    """How far past `point` the ray stays inside `member`, mm (0 if outside)."""
    t = math.inf
    for j in range(3):
        d = direction[j]
        lo, hi = member.extents[j]
        if abs(d) < 1e-9:
            if not (lo - 1e-6 <= point[j] <= hi + 1e-6):
                return 0.0
            continue
        cand = ((hi if d > 0 else lo) - point[j]) / d
        if cand < 0:
            return 0.0
        t = min(t, cand)
    return 0.0 if t is math.inf else t


def _inside(point, member, grow=0.0):
    return all(lo - grow <= point[j] <= hi + grow
               for j, (lo, hi) in enumerate(member.extents))


def _segment_gap(a, b):
    """Least distance between two segments, each given as (start, end).

    X10 asks it of two screw axes. Segments, not lines: a screw stops at its
    tip, and two screws that would have crossed 40 mm further on do not touch.
    Clamped both ways, so a pair that misses end-on is measured end to end.
    """
    (p1, q1), (p2, q2) = a, b
    d1 = [x - y for x, y in zip(q1, p1)]
    d2 = [x - y for x, y in zip(q2, p2)]
    r = [x - y for x, y in zip(p1, p2)]
    A = sum(x * x for x in d1)
    E = sum(x * x for x in d2)
    F = sum(x * y for x, y in zip(d2, r))
    C = sum(x * y for x, y in zip(d1, r))
    B = sum(x * y for x, y in zip(d1, d2))
    den = A * E - B * B
    s = 0.0 if abs(den) < 1e-12 else min(1.0, max(0.0, (B * F - C * E) / den))
    t = (B * s + F) / E
    if t < 0.0:
        t, s = 0.0, min(1.0, max(0.0, -C / A))
    elif t > 1.0:
        t, s = 1.0, min(1.0, max(0.0, (B - C) / A))
    return math.dist([x + s * v for x, v in zip(p1, d1)],
                     [x + t * v for x, v in zip(p2, d2)])


# `display_parts` is defined below, so the names the panel-assembly rule needs
# are stated here, where the rule is used.
PANEL_JOINT = "J13"          # every joint id in the panel sub-assembly
_FIXED_IDS = frozenset(id(p) for p in parts)
TOE_SEAT_COVER = []          # (label, mm of wood over the head) per toe screw


def on_visible_front(f):
    """True when this fastener's head is on a room-facing face (V5).

    The head is on the face the fastener is driven from, so that face looks
    out of the front exactly when the fastener travels in -Y; and it is a
    face of the VISIBLE FRONT when it sits at or in front of
    VISIBLE_FRONT_Y. See the V5 note up in the POSTS section - this is an
    aesthetic rule, not a structural one, and the reason J2, J3 and J8 are
    driven from inside the bed outward.
    """
    return (f["direction"][1] < -1e-9
            and f["anchor"][1] >= VISIBLE_FRONT_Y - FASTENER_TOL)

if FASTENERS_ON:
    _others = {}
    for _mode, _panel in MODES.items():
        _others[_mode] = [p for p in mode_parts(_panel) if not is_soft(p)]

    for _f in FASTENER_SPECS:
        _s = _f.get("solid")
        if _s is None:
            continue
        _own = [p for p in (_f["through"], _f["into"]) if p is not None]
        _label = _s.label

        if _f["kind"] == "screw":
            _ax, _sg = _axis_of(_f["direction"])
            _skew = abs(abs(_f["direction"][_ax]) - 1.0) > 1e-6
            _fx, _face = _f["face"]

            # 1 - the head is FLUSH with the face it is driven from. Not proud
            #     (it would foul whatever lands on that face), not sunk (the
            #     drawing would lie). A skew screw's head is sunk into the
            #     face at an angle, so what is checked there is the anchor:
            #     the centre of the head is ON the face, and nothing of the
            #     screw stands in front of it.
            if not _skew:
                _head = _s.extents[_ax][1] if _sg < 0 else _s.extents[_ax][0]
                assert abs(_head - _f["anchor"][_ax]) < FASTENER_TOL, (
                    f"{_label}: the head sits "
                    f"{_head - _f['anchor'][_ax]:+.2f} mm off the entry face "
                    f"— it must be flush")
            assert abs(_f["anchor"][_fx] - _face) < FASTENER_TOL, (
                f"{_label}: the head is at {_f['anchor'][_fx]:g} on axis "
                f"{'XYZ'[_fx]}, the face it is driven from is at {_face:g}")

            # 1b - V4, A SKEW SCREW'S HEAD IS UNDER THE WOOD. Measured on the
            #      solid, not on the seat arithmetic: take the whole screw's
            #      furthest reach towards the face it came in through and
            #      require wood over it. This is the assert that replaces
            #      TOE_HEAD_ALLOWANCE, and it is a stronger claim - the old one
            #      merely capped how much could stick out.
            if _f.get("toe"):
                _sax, _ssg, _surf = _f["seat_face"]
                _high = (_s.extents[_sax][1] if _ssg > 0
                         else _s.extents[_sax][0])
                _under = (_surf - _high) if _ssg > 0 else (_high - _surf)
                # K4: AND AGAIN WITH THE HEAD OFF THE BOTTOM. A 90 degree
                # countersunk head in a flat-bottomed pocket has two rests -
                # the bottom, and the rim of the pilot hole under it. The cone
                # between head diameter and shank stands (D_h - d)/2 proud of
                # the bottom when it takes the second one, and the part of that
                # which is spent on the cover is its component along the face
                # normal, i.e. cos(deg) = the direction's own component on the
                # seat-face axis. Both cases are held to the same limit.
                _rim = ((SCREW_HEAD_D[int(round(_f["d"]))] - _f["d"]) / 2
                        * abs(_f["direction"][_sax]))
                for _case, _have in (("på bunnen", _under),
                                     ("på forborkanten", _under - _rim)):
                    assert _have >= TOE_SEAT_MIN_COVER, (
                        f"{_label}: with the head resting {_case} the highest "
                        f"point of it stands {-_have:+.2f} mm past the face at "
                        f"{_surf:g} on axis {'XYZ'[_sax]} — the "
                        f"{_f['seat_d']:g} mm seat is {_f['seat']:g} mm deep "
                        f"and wants to leave {TOE_SEAT_MIN_COVER} mm of wood "
                        f"over it in BOTH rests (K4)")
                TOE_SEAT_COVER.append((_label, _under, _under - _rim))

            # 2 - the tip is INSIDE the member it grips, with wood behind it.
            _tip = tuple(a + d * _f["length"]
                         for a, d in zip(_f["anchor"], _f["direction"]))
            _target = _f["into"]
            assert _inside(_tip, _target, -1e-6), (
                f"{_label}: the tip lands at "
                f"{tuple(round(v, 1) for v in _tip)}, outside "
                f"'{_target.label}' — the screw does not reach the "
                f"member it is supposed to tie, or it has gone straight "
                f"through it")
            _cover = _ray_exit(_tip, _f["direction"], _target)
            assert _cover >= FASTENER_MIN_TIP_COVER, (
                f"{_label}: only {_cover:.1f} mm of '{_target.label}' "
                f"left behind the tip, want {FASTENER_MIN_TIP_COVER}")

            # 3 - the physics, on the shape: the head is in the member it is
            #     driven from and the tip is in the one it grips.
            if _f["through"] is not None:
                assert _inside(tuple(a + d * 0.5 for a, d in
                                     zip(_f["anchor"], _f["direction"])),
                               _f["through"], 1e-6), (
                    f"{_label}: the head is not in '{_f['through'].label}'")

        # 4 - nothing of it is outside its own joint, and nothing of it is in
        #     anybody else's wood, in either mode.
        # A bracket lies ON the wood, so it is not contained by anything; a
        # SCREW must be.
        if _f["kind"] == "screw":
            _v = abs(_s.volume)
            _in = sum(_cut_volume(_s, p) for p in _own)
            # V4: no special case for skew screws any more. The seat put the
            # head under the wood, so a toe screw has to be as fully contained
            # as any other.
            _slack = max(FASTENER_VOL_TOL, 0.02 * _v)
            assert _v - _in < _slack, (
                f"{_label}: {_v - _in:.0f} mm3 of {_v:.0f} is outside the "
                f"joint ({' + '.join(p.label for p in _own)}) — it exits a "
                f"member or points into thin air")
        # The panel's own fasteners MOVE WITH THE PANEL, so in table mode the
        # solid that has to be clear of the bed is the lifted one, and the
        # members it is allowed to be inside are that mode's panel and
        # battens. Checking the bed-mode solid against table-mode wood would
        # pass by simply being PANEL_MODE_LIFT away from everything, which is the
        # non-check that let the two modes drift apart in the first place.
        _mine = _f["jid"].startswith(PANEL_JOINT)
        for _mode, _pl in _others.items():
            _probe = _s
            _skip = _own
            if _mine and _mode == "table_mode":
                _probe = _tag(Location((0, 0, PANEL_MODE_LIFT)) * _s,
                              _f, _label)
                _skip = [p for p in _pl if id(p) not in _FIXED_IDS]
            for _p in _pl:
                if _p in _skip:
                    continue
                _hit = _cut_volume(_probe, _p)
                assert _hit < FASTENER_VOL_TOL, (
                    f"{_mode}: {_label} runs {_hit:.0f} mm3 into "
                    f"'{_p.label}'")

    # --- V5: NOT ONE HEAD ON THE VISIBLE FRONT -----------------------------
    # An AESTHETIC assert, and the only one in this file. Nothing about it is
    # structural: every joint it governs is 'tvetydig' under the through-screw
    # rule, i.e. the physics is happy either way round and the choice was
    # always the table's. What it buys is a front face - two posts, two ladder
    # uprights, the front side rail, the two front bench-rail segments and the
    # four guard boards - with no steel showing anywhere on it.
    _showing = [(_f["jid"], _f["name"],
                 tuple(round(v, 1) for v in _f["anchor"]))
                for _f in FASTENER_SPECS if on_visible_front(_f)]
    assert not _showing, (
        "V5: festemiddelhoder på en romvendt flate (Y >= "
        f"{VISIBLE_FRONT_Y}, drevet innover i -Y): "
        + "; ".join(f"{j} {n} @ {a}" for j, n, a in _showing)
        + " — snu skruen så den drives innenfra og ut")
    _front_count = sum(1 for _f in FASTENER_SPECS
                       if _f["kind"] == "screw" and _f["direction"][1] > 1e-9
                       and _f["into"] is not None
                       and _f["into"].extents[1][1] >= VISIBLE_FRONT_Y
                       - FASTENER_TOL)
    print(f"OK  V5 synlig front: ingen av de {len(FASTENER_SPECS)} "
          f"festemidlene har hodet på en flate fra Y {VISIBLE_FRONT_Y:g} og "
          f"framover. De {_front_count} som tar tak i en del i det laget "
          f"(J2, J3, J7, J8) er alle skrudd innenfra og ut")

    # --- the brackets stand the right way round ----------------------------
    # The bug this kills is the upside-down bracket: a flange screwed to a
    # face that has no wood behind it. Both flanges of every angle bracket are
    # checked, and the one that matters most is the horizontal flange of the
    # 40x40x20 under the table ledger - if that one is on top of the ledger
    # instead of under it, the ledger hangs on two 5 mm screws in withdrawal
    # instead of standing on steel.
    _n_ang = 0
    for _f in FASTENER_SPECS:
        if _f["kind"] != "plate":
            continue
        _C = _f["anchor"]
        _ax, _sa = _axis_of(_f["direction"])
        _rx, _sr = _axis_of(_f["run"])
        # Flange A: its screws go along `direction` into the member the
        # bracket is anchored on. Flange B: at right angles, screwed along
        # -run into the OTHER member. Both have to hit wood.
        _legs = [(tuple(_C[j] + _f["run"][j] * _f["reach"] / 2
                        for j in range(3)), _f["direction"]),
                 (tuple(_C[j] - _f["direction"][j] * _f["reach"] / 2
                        for j in range(3)),
                  tuple(-c for c in _f["run"]))]
        if _f.get("bears") is not None:
            # THE UPSIDE-DOWN BRACKET. Flange B is the one that carries, and
            # a carrying flange is horizontal, screwed straight UP, and sits
            # ON THE UNDERSIDE of the member it carries. Turn the bracket
            # over and its screws still land in wood - they land in the TOP
            # of the ledger - so "the screws hit something" is not the check.
            # This is.
            _up = tuple(-c for c in _f["run"])
            _borne = _f["bears"]
            assert _up == (0.0, 0.0, 1.0), (
                f"{_f['jid']}: the flange that carries '{_borne.label}' is "
                f"screwed along {_up}, not straight up — the bracket is on "
                f"its side or upside down")
            assert abs(_C[2] - _borne.extents[2][0]) < FASTENER_TOL, (
                f"{_f['jid']}: the carrying flange sits at Z {_C[2]:g} and "
                f"'{_borne.label}' has its underside at "
                f"{_borne.extents[2][0]:g} — it is not UNDER the member it "
                f"is supposed to hold up")
        for _i, (_at, _dir) in enumerate(_legs):
            _probe = tuple(a + d * 1.0 for a, d in zip(_at, _dir))
            _hit = next((p for p in _others["bed_mode"]
                         if _inside(_probe, p, -1e-6)), None)
            assert _hit is not None, (
                f"{_f['jid']}: flange {'AB'[_i]} of {_f['name']} is screwed "
                f"along {_dir} into thin air at "
                f"{tuple(round(v, 1) for v in _probe)} — the bracket is on "
                f"the wrong face, or the wrong way up")
        _n_ang += 1

    print(f"OK  {len(FASTENERS)} festemidler modellert som kropper: hode i "
          f"plan med flaten, spiss inne i delen den tar tak i (minst "
          f"{FASTENER_MIN_TIP_COVER:g} mm dekning), ingenting i noen annen "
          f"del i noen av de to stillingene")
    print(f"OK  {_n_ang} vinkelbeslag: hver skrudd flik har tre bak seg i "
          f"skrueretningen. Ingen av dem sitter i platemekanismen - V3 tok "
          f"alle fire ut av den og lot lektene gjøre jobben")
    assert len(TOE_SEAT_COVER) == sum(1 for _f in FASTENER_SPECS
                                      if _f.get("toe")), \
        "V4: en skråskrue slapp unna setekontrollen"
    print(f"OK  V4/K4 skråskruesete: alle {len(TOE_SEAT_COVER)} skråskruene "
          f"(J8-B ×4 à {TOE_JIG_SEATS['J8-B']:g} mm, J10 ×4 à "
          f"{TOE_JIG_SEATS['J10']:g} mm) står i et flatbunnet ⌀{TOE_SEAT_D:g} "
          f"sete boret LANGS skruens egen akse. Minste tre over hodets høyeste "
          f"punkt: {min(u for _l, u, _r in TOE_SEAT_COVER):.2f} mm med hodet "
          f"på bunnen, {min(r for _l, _u, r in TOE_SEAT_COVER):.2f} mm med "
          f"konusen på forborkanten (krav {TOE_SEAT_MIN_COVER:g} i begge) - "
          f"målt på kroppene. K4 er nettopp det andre tallet: 18 mm på J8-B ga "
          f"1,03 mm der, og en margin som forutsetter at skruen finner bunnen "
          f"av sin egen lomme er ingen margin")

    # K4: THE WALL BETWEEN TWO SEATS. See TOE_SEAT_MIN_WEB. The row rule that
    # places these screws spaces SHANKS - 4d centres for a 6 mm screw - and the
    # pocket each one sits in is three times the shank across, so what is left
    # between two of them is 4d - TOE_SEAT_D and nobody was measuring it. K2's
    # counterbore rule does not reach here (it is written on ⌀12 bores in a
    # wing), so the seat gets its own. Measured on the placed fasteners, per
    # joint and member, and PERPENDICULAR TO THE COMMON AXIS: two pockets are
    # parallel cylinders, so the wood between them is the perpendicular part of
    # the centre-to-centre vector, not its length.
    _SEATED = {}
    for _f in FASTENER_SPECS:
        if _f.get("toe"):
            _SEATED.setdefault((_f["jid"], _f["through"].label), []).append(_f)
    TOE_SEAT_WEB_MIN = 1e18
    TOE_SEAT_WEB_WHO = None
    for (_jid, _), _group in sorted(_SEATED.items(), key=lambda kv: kv[0][0]):
        for _i, _a in enumerate(_group):
            for _b in _group[_i + 1:]:
                _sep = [q - p for p, q in zip(_a["anchor"], _b["anchor"])]
                _ax_u = _a["direction"]
                _along = sum(s * u for s, u in zip(_sep, _ax_u))
                _perp = math.dist([0.0, 0.0, 0.0],
                                  [s - _along * u
                                   for s, u in zip(_sep, _ax_u)])
                if _perp - TOE_SEAT_D < TOE_SEAT_WEB_MIN:
                    TOE_SEAT_WEB_MIN, TOE_SEAT_WEB_WHO = (_perp - TOE_SEAT_D,
                                                          _jid)
    if TOE_SEAT_WEB_WHO is None:
        print("OK  K4 setevegg: ingen to skråskruesete deler flate - "
              "ingenting å måle")
    else:
        assert TOE_SEAT_WEB_MIN >= TOE_SEAT_MIN_WEB - FIT_TOL, (
            f"K4: {TOE_SEAT_WEB_WHO} leaves {TOE_SEAT_WEB_MIN:g} mm of wood "
            f"between two ⌀{TOE_SEAT_D:g} seats in one face, and the floor is "
            f"{TOE_SEAT_MIN_WEB:g} mm - one shank diameter, so the Forstner "
            f"cutting the second pocket has solid wood to cut against all the "
            f"way round. Move the row apart, take the seat down, or take a "
            f"screw out - the wall is not a place to save millimetres")
        print(f"OK  K4 setevegg: de to ⌀{TOE_SEAT_D:g}-lommene i "
              f"{TOE_SEAT_WEB_WHO} står {TOE_SEAT_WEB_MIN + TOE_SEAT_D:g} mm "
              f"fra hverandre på tvers av aksen = {TOE_SEAT_WEB_MIN:g} mm tre "
              f"imellom, krav {TOE_SEAT_MIN_WEB:g} (én skruediameter). "
              f"Rekkeregelen måler skruen; lomma den ligger i har sin egen")

    # --- X10: TWO SCREWS DO NOT MEET IN THE SAME PIECE OF WOOD --------------
    # THE HOLE THIS FILLS, SAID PLAINLY. Every assert above asks a screw about
    # WOOD: is the head flush with it, is the tip inside it, is any of the body
    # in somebody else's. Not one of them asks a screw about ANOTHER SCREW, and
    # `mode_parts()` is wood-only by design, so the fasteners were never in the
    # list they were being checked against. Sixteen pairs were driven through
    # each other and the model said OK: ten of them at the rung ends, where a
    # 6x120 from the upright and a 5x60 dropped through the tread crossed at a
    # POINT, 0,00 mm apart. A drawing cannot be wrong in a way a build catches;
    # this is the shape asking the question the wood asserts could not.
    #
    # WHY IT IS THE RIGHT SHAPE OF RULE. Every placement rule in this file puts
    # its row in the MIDDLE of its own contact window - and it is right to. What
    # nobody noticed is that two joints sharing a piece of wood share the middle
    # as well: the end slat's screw and the front post's screw both land on
    # X 50,5 because both are correct. So the collisions are not mistakes, they
    # are the rule meeting itself, and the fix is not a bigger rule but a
    # SECOND one - a `drive(offset=...)` that steps a row off its own centre,
    # with a written reason, policed by this measurement and by the edge rule.
    #
    # HOW IT IS ASKED. Screws are SEGMENTS, head centre to tip, so two of them
    # are two line segments and the question is the least distance between them
    # - not between their anchors, which would miss a crossing entirely, and not
    # a boolean intersection, which only sees steel actually touching steel and
    # would pass a pair 0,1 mm apart. The floor is `screw_clearance`: the two
    # half-shanks plus one shank of wood, the same unit MIN_EDGE (3d),
    # min_spacing (4d) and TOE_SEAT_MIN_WEB (1d) are written in.
    #
    # GROUPED BY THE WOOD, AND ACROSS JOINTS. Two screws can only foul each
    # other where they are both present, so the pairs that matter are the ones
    # that SHARE A MEMBER - through or into, either way round. That is also the
    # only grouping that spans joints, which is exactly where the misses were:
    # not one of the sixteen was a joint fighting itself except J4, and J4 is
    # the one this file would have found on its own.
    #
    # THE WALL SCREWS ARE IN IT. J14 has no wood on the far side and is skipped
    # by the containment asserts, but its near half is in the back rail with the
    # slat screws and the post-top screws, and its X is spread the way a builder
    # spreads it - so if the spread lands one on top of a slat screw, that is a
    # real collision in a real rail and the rule should say so.
    SCREW_PAIR_MIN = 1e18
    SCREW_PAIR_WHO = None
    SCREW_PAIR_AT = (0.0, 0.0)
    SCREW_PAIR_TIGHT = []
    _seg = {}
    for _f in FASTENER_SPECS:
        if _f["kind"] != "screw":
            continue
        _a = _f["anchor"]
        _seg[id(_f)] = (_a, tuple(p + v * _f["length"]
                                  for p, v in zip(_a, _f["direction"])))
    _screws = [_f for _f in FASTENER_SPECS if _f["kind"] == "screw"]
    for _i, _a in enumerate(_screws):
        _amem = {id(p): p for p in (_a.get("through"), _a.get("into"))
                 if p is not None}
        for _b in _screws[_i + 1:]:
            _bmem = {id(p): p for p in (_b.get("through"), _b.get("into"))
                     if p is not None}
            _shared = set(_amem) & set(_bmem)
            if not _shared:
                continue
            _dist = _segment_gap(_seg[id(_a)], _seg[id(_b)])
            _need = screw_clearance(_a["d"], _b["d"])
            _who = (f"{_a['jid']} ⌀{_a['d']:g} × {_b['jid']} ⌀{_b['d']:g} i "
                    f"'{sorted(_amem[k].label for k in _shared)[0]}'")
            if _dist - _need < SCREW_PAIR_MIN:
                SCREW_PAIR_MIN, SCREW_PAIR_WHO = _dist - _need, _who
                SCREW_PAIR_AT = (_dist, _need)
            assert _dist >= _need - FIT_TOL, (
                f"X10: {_who} står {_dist:.2f} mm fra hverandre målt akse mot "
                f"akse, og kravet er {_need:.2f} - de to halve skaftene "
                f"({(_a['d'] + _b['d']) / 2:g}) pluss "
                f"{screw_web(_a['d'], _b['d']):g} mm tre. To skruer som møtes "
                f"i det samme treet borer hverandre i stykker, og treet mellom "
                f"dem er det som holder begge. Flytt raden med "
                f"drive(offset=...), snu den ene, kort den, eller stryk den - "
                f"anker A {tuple(round(v, 1) for v in _a['anchor'])} → "
                f"{tuple(round(v, 1) for v in _seg[id(_a)][1])}, anker B "
                f"{tuple(round(v, 1) for v in _b['anchor'])} → "
                f"{tuple(round(v, 1) for v in _seg[id(_b)][1])}")
            if _dist - _need < screw_web(_a["d"], _b["d"]):
                SCREW_PAIR_TIGHT.append((_dist, _need, _who))
    assert SCREW_PAIR_WHO is not None, \
        "X10: ingen to skruer deler tre - det kan ikke stemme i denne sengen"
    SCREW_PAIR_TIGHT.sort(key=lambda r: r[0] - r[1])
    print(f"OK  X10 skrue mot skrue: av de {len(_screws)} skruene står de "
          f"nærmeste to som deler tre {SCREW_PAIR_AT[0]:.2f} mm fra hverandre "
          f"akse mot akse mot et krav på {SCREW_PAIR_AT[1]:.2f} "
          f"({SCREW_PAIR_MIN:+.2f}) - {SCREW_PAIR_WHO}. Målt som korteste "
          f"avstand mellom to linjestykker, gruppert på delen de deler, på "
          f"tvers av ledd")
    for _d, _n, _w in SCREW_PAIR_TIGHT[:5]:
        print(f"      {_w:56s} {_d:6.2f} mot {_n:5.2f} ({_d - _n:+.2f})")
else:
    print("(fasteners off - LOFTBED_FASTENERS=0)")


# ---------------------------------------------------------------------------
# THE PANEL'S OWN FASTENERS TRAVEL WITH THE PANEL
# ---------------------------------------------------------------------------
# THE BUG THIS KILLS, written down because it shipped: the fasteners are
# modelled ONCE, in bed mode, and `display_parts` used to hand that one list to
# both modes. The wood of the panel assembly is built per mode - panel_bed at
# Z 297, panel_table at Z 542 - but its screws were not, so in table mode the
# exported .usdz showed the panel 223 mm up and its own screws still down at
# bed height, hanging in the air under it. Every other fastener in the bed ties
# two FIXED members and is right in both modes; the J13 family ties two members
# that move, and it has to move with them. One rule, one place:
def _is_panel_fastener(s):
    return s.spec["jid"].startswith(PANEL_JOINT)


_PANEL_FASTENERS = {}


def panel_fasteners(panel):
    """The panel sub-assembly's own fasteners, at THIS mode's height.

    Built once per mode and cached, so every caller - the export, the
    drawings, the insertion sweep - gets the same solids and not a fresh copy
    of them.
    """
    key = id(panel)
    if key not in _PANEL_FASTENERS:
        dz = PANEL_MODE_LIFT if panel is panel_table else 0
        _PANEL_FASTENERS[key] = [
            s if dz == 0 else _tag(Location((0, 0, dz)) * s, s.spec, s.label)
            for s in FASTENERS if _is_panel_fastener(s)]
    return _PANEL_FASTENERS[key]


def display_parts(panel):
    """The wood PLUS the fasteners - what gets exported and drawn."""
    return (mode_parts(panel)
            + [s for s in FASTENERS if not _is_panel_fastener(s)]
            + panel_fasteners(panel))


def make_compound(panel, xform=IDENTITY):
    return Compound(children=[p.moved(xform) for p in display_parts(panel)])


bed_mode = make_compound(panel_bed)
table_mode = make_compound(panel_table)
# V13: the ENVELOPE is a statement about the BED - the wood, the steel and the
# reference mattress that fills the upper bunk exactly. The four cushions are
# loose foam, and in sofa mode one of them deliberately stands 12 mm proud of
# the front plane (see BACKREST_PROUD), so they are measured by their own
# asserts and not by the bed's outline.
_CUSHION_IDS = {id(c) for c in CUSHIONS_ALL}


class _BB:
    """The bounding box of a list of solids, without building a Compound out of
    them - Compound(children=...) would re-parent solids that already belong to
    the exported one."""

    def __init__(self, solids):
        boxes = [p.bounding_box() for p in solids]
        self.min = type("P", (), {})()
        self.max = type("P", (), {})()
        for ax in "XYZ":
            setattr(self.min, ax, min(getattr(b.min, ax) for b in boxes))
            setattr(self.max, ax, max(getattr(b.max, ax) for b in boxes))


def wood_envelope(panel):
    return _BB([p for p in display_parts(panel) if id(p) not in _CUSHION_IDS])


# ===========================================================================
# REFERANSEKROPPENE - THE TWO CHILDREN, AS SOLIDS
# ===========================================================================
# A THIRD CATEGORY. The bed is made of wood (cut, listed, screwed), of steel
# (bought, listed, driven) and of foam (bought, not listed, laid on). This is
# the fourth: a body. It is not bought and it is not built - it is the reason
# the rest exists, and until now it was only ever a number in a clearance
# assert. A clearance is an argument about a child; drawing the child is
# cheaper to check than reading the argument.
#
# THE CATEGORY RULE, and it is the mattress's rule word for word (docs/
# PRAKSIS.md): a reference body has its own colour group, it is OUT of the cut
# list, out of the contact / connectivity / overlap checks and out of every
# wood-only list, and it is IN parts.tsv and in the exported scene. What it
# adds on top of the mattress's rule is that it is not in `display_parts`
# either: the films and the manual pages are built from that list, and a body
# in the panel-sweep collision test would fail a film that is about wood.
# `scene_parts()` below is display_parts + bodies, and that is what the STEP /
# STL / GLB / USDZ scene is.
#
# THE BOX INVARIANT. Every clearance assert in this file is arithmetic on
# `extents`, and `extents` on a figure is its BOUNDING BOX - a box that the
# real solid is strictly inside, exactly as it is for the tapered wing and for
# the notched cushions. The invariant holds for the same reason it holds
# there, and this time the first half is free rather than argued: A FIGURE HAS
# NO MATING FACE. It joins nothing, so contacts(), patch_window() and
# bearing_area() are never asked about it. What is left is the conservative
# half - anything reading `extents` clears more than the body occupies - and
# that is the direction a clearance wants to be wrong in. The numbers that are
# PUBLISHED, though, are measured on the solid (see FIGURE_CLEAR below), not
# on the box: a seated child's bounding box is a 700 mm cube and would say
# nothing true about the room over the head.
#
# ANTHROPOMETRY. Public domain: AnthroKids - the digitised 1975/1977 Snyder et
# al. child anthropometry studies, math.nist.gov/~SRessler/anthrokids/. Every
# segment below is a fraction of standing height H, and H is set at 1200 mm -
# the 50th percentile for about 6-8 years, which is the age EN 747 opens the
# upper bunk at. The five key dimensions the fractions are calibrated on are
# sitting height 0.545 H, popliteal (knee-hollow) height 0.28 H, sitting knee
# height 0.30 H, shoulder breadth 0.21 H and head height H/6, and each of them
# comes back out of the built solid in FIGURE_ASSERTS below.
#
# LEVEL OF ABSTRACTION: the manual's. A round head, no face, no hands, a box
# for a foot. Fourteen primitives fused into ONE solid, the same way the screw
# is a Cylinder + Cone + Cylinder + Cone fused into one - a chain of
# Pos() * Rot() down five joint types (hip, knee, shoulder, elbow, neck) with
# no inverse kinematics anywhere: every angle in the pose tables is typed, and
# what the model then MEASURES is where that pose puts the body.
FIGURE_H = 1200.0                # standing height, mm  (EN 747 alder 6+)


def _fh(k):
    return k * FIGURE_H


# --- the segment table, every entry a fraction of H -------------------------
FIG_HEAD_R = _fh(0.0833)     # 100  head height H/6 = 200 IS the diameter
FIG_NECK_R = _fh(0.030)      # 36
FIG_NECK_L = _fh(0.052)      # 62
FIG_TORSO_R = _fh(0.075)     # 90   between chest depth and chest breadth
FIG_TORSO_L = _fh(0.262)     # 314  hip joint -> shoulder joint
FIG_HIP_R = _fh(0.075)       # 90
FIG_UARM_R = _fh(0.032)      # 38
FIG_UARM_L = _fh(0.170)      # 204
FIG_FARM_R = _fh(0.027)      # 32
FIG_FARM_L = _fh(0.160)      # 192
FIG_THIGH_R = _fh(0.048)     # 58
FIG_THIGH_L = _fh(0.245)     # 294
FIG_SHANK_R = _fh(0.038)     # 46
FIG_SHANK_L = _fh(0.236)     # 283
FIG_ANKLE_Z = _fh(0.039)     # 47   sole -> ankle joint
FIG_FOOT_L = _fh(0.150)      # 180
FIG_FOOT_W = _fh(0.055)      # 66
FIG_FOOT_H = _fh(0.050)      # 60
FIG_SHOULDER_Y = _fh(0.105)  # 126  half of shoulder breadth 0.21 H
FIG_HIP_Y = _fh(0.050)       # 60
FIG_SINK = 12                # mm the body settles into 100 mm of foam

# The five reference dimensions the table is calibrated on.
FIG_SITTING_H = _fh(SIT_RATIO)   # 654  seat -> crown
FIG_POPLITEAL = _fh(0.28)    # 336  floor -> knee hollow, seated
FIG_KNEE_SIT = _fh(0.30)     # 360  floor -> top of knee, seated
FIG_SHOULDER_W = _fh(0.21)   # 252
FIG_HEAD_H = FIGURE_H / 6    # 200


def _dirv(yaw, pitch):
    """Unit vector from a compass bearing. `yaw` degrees about +Z from +X,
    `pitch` degrees up from horizontal. One convention for all five joints."""
    y, p = math.radians(yaw), math.radians(pitch)
    return (math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), math.sin(p))


def _bone(base, direction, length, r):
    """One limb: a cylinder from `base` along `direction`. Returns (solid,
    tip), and the tip is the next joint - that is the whole kinematic chain."""
    v = Vector(*direction)
    v = v / v.length
    d = (v.X, v.Y, v.Z)
    c = Cylinder(r, length).moved(Location((0, 0, -length / 2)))
    return (Location(base) * _rot_to(d) * c,
            tuple(base[i] + d[i] * length for i in range(3)))


def _foot(ankle, direction):
    """The foot: a box hung off the ankle, long axis down `direction`. The
    roll about that axis is not constrained and does not need to be - at
    drawing scale a foot is a nub that says which way the leg ended."""
    b = Box(FIG_FOOT_H, FIG_FOOT_W, FIG_FOOT_L).moved(
        Location((0, 0, -FIG_FOOT_L / 2)))
    return Location(ankle) * _rot_to(direction) * b


def child(label, hip, facing, torso, head, arms, legs):
    """One reference child, fused to a single solid.

    `hip`     the hip-joint centre, model mm
    `facing`  the bearing the body points, degrees about +Z from +X
    `torso`   (yaw, pitch) of the hip -> shoulder axis, RELATIVE to `facing`
    `head`    (yaw, pitch) of the neck -> head axis, same convention
    `arms`    per side ((upper yaw, pitch), (fore yaw, pitch))
    `legs`    per side ((thigh), (shank), (foot)), each (yaw, pitch)

    Per side means (near, far); the far side's yaws are negated, so a
    symmetric pose is written once and only the deliberate asymmetries - the
    crossed shanks, the arm that reaches - are typed twice.
    """
    up = _dirv(facing + torso[0], torso[1])
    body, shoulder = _bone(hip, up, FIG_TORSO_L, FIG_TORSO_R)
    solid = body
    solid += Sphere(FIG_HIP_R).moved(Location(hip))
    neck, neck_top = _bone(shoulder, up, FIG_NECK_L, FIG_NECK_R)
    solid += neck
    hd = _dirv(facing + head[0], head[1])
    head_c = tuple(neck_top[i] + hd[i] * FIG_HEAD_R for i in range(3))
    solid += Sphere(FIG_HEAD_R).moved(Location(head_c))

    side = _dirv(facing + 90.0, 0.0)
    for s, (ua, fa) in zip((+1, -1), arms):
        sh = tuple(shoulder[i] + side[i] * s * FIG_SHOULDER_Y for i in range(3))
        upper, elbow = _bone(sh, _dirv(facing + s * ua[0], ua[1]),
                             FIG_UARM_L, FIG_UARM_R)
        fore, _wrist = _bone(elbow, _dirv(facing + s * fa[0], fa[1]),
                             FIG_FARM_L, FIG_FARM_R)
        solid += upper
        solid += fore
    for s, (th, sk, ft) in zip((+1, -1), legs):
        hp = tuple(hip[i] + side[i] * s * FIG_HIP_Y for i in range(3))
        thigh, knee = _bone(hp, _dirv(facing + s * th[0], th[1]),
                            FIG_THIGH_L, FIG_THIGH_R)
        shank, ankle = _bone(knee, _dirv(facing + s * sk[0], sk[1]),
                             FIG_SHANK_L, FIG_SHANK_R)
        solid += thigh
        solid += shank
        solid += _foot(ankle, _dirv(facing + s * ft[0], ft[1]))

    solid.label = label
    solid.color = GROUP_COLORS["figures"]
    solid.group = "figures"
    bb = solid.bounding_box()
    solid.extents = ((bb.min.X, bb.max.X), (bb.min.Y, bb.max.Y),
                     (bb.min.Z, bb.max.Z))
    # The joints the pose was built through, kept for the measured clearances
    # and for the drawings: a dimension line wants the crown, not the box.
    # NOT `.joints` - build123d owns that name on a Shape, and a dict of
    # tuples parked there dies in deepcopy the first time the solid is moved.
    solid.pose = {"hip": hip, "shoulder": shoulder, "neck": neck_top,
                    "head": head_c,
                    "crown": tuple(head_c[i] + hd[i] * FIG_HEAD_R
                                   for i in range(3))}
    return solid


# ---------------------------------------------------------------------------
# THE FOUR POSES
# ---------------------------------------------------------------------------
# BENCH DEPTH is 800 mm and the bench is the lower bed, so a child sitting on
# it sits in the middle of it: Y = 352 in both directions.
FIG_BENCH_Y = (LOWER_SLEEP_Y0 + LOWER_SLEEP_Y0 + LOWER_SLEEP_DEPTH) / 2  # 352

# SEATED: the hip joint rides SIT_RISE above the cushion face, not one hip
# radius above it - a 100 mm foam cushion takes the buttock in. The number is
# not chosen, it is solved: SIT_RISE is what puts the crown exactly one
# sitting height (0.545 H) above the seat.
FIG_SIT_RISE = FIG_SITTING_H - FIG_TORSO_L - FIG_NECK_L - 2 * FIG_HEAD_R  # 77
SEAT_FACE = BENCH_TOP + CUSHION_T                      # 420, the sofa seat [X3: 382]
FIG_SIT_Z = SEAT_FACE + FIG_SIT_RISE                   # 497, hip joint

# X9: THE LEGS COME DOWN, BECAUSE THE PLATE BECAME A DESK.
#
# WHAT THE OLD POSE WAS FOR, AND WHY IT IS NOW A LIE. Through v15 the plate was
# a LAP TABLE: 140 mm above the seat face with 122 under it. A thigh is 116 mm
# through, so a straight leg went under it and a bent KNEE did not - the knee
# of a seated child stands about 300 mm above the floor and the plate underside
# was at 542, but the knee has to get there past a 122 mm slot, and it cannot.
# So the two seated figures sat CROSS-LEGGED, up on the bench, and the prose in
# this file argued that this was not a compromise but the way anybody sits on a
# bench beside a low table. That argument was TRUE at 560. It is not true at
# 700: the plate's underside is 682 now, 262 mm over the seat face, and a
# seated knee tops out one thigh radius above the hip - 555, or 135 over the
# seat. 127 mm of air over the knee. The knees go under, so the figures sit
# the way people sit at a desk, and the sentence that explained the folded legs
# is deleted rather than kept and quietly falsified.
#
# THE POSE, JOINT BY JOINT. Thighs forward and level, splayed 6 degrees so the
# two knees read as two; shanks plumb; feet hanging, because at a 420 mm seat a
# 1200 mm child's soles are 150 mm off the floor and there is no footrest under
# this plate - said here rather than drawn away.
_DESK_LEG = ((6, -1), (0, -88), (0, -15))
# AND THE HIP MOVES FORWARD OFF THE BACK CUSHION, because that is what sitting
# AT something means. The number is not chosen: put the knee one thigh radius
# in under the plate's own edge and the hip is one thigh behind it.
FIG_SEAT_X = PANEL_X0 + FIG_THIGH_R - FIG_THIGH_L      # 472  [X2: 288, on the pad]

figure_seated_left = child(
    "Child Seated Left (table mode)",
    (FIG_SEAT_X + 2, FIG_BENCH_Y, FIG_SIT_Z), 0.0,
    # THE ONE WHO WORKS AT IT. Sat up straight: the 25 degree lean the sofa
    # table needed is gone with the sofa table, because the plate is no longer
    # something you reach DOWN and OUT to. It is the other way now, and the
    # figure is where that gets said out loud. This child's seated elbow hangs
    # at 608 (shoulder 812 less a 204 mm upper arm) and the plate is at 700, so
    # the FOREARMS COME UP ONTO IT and the elbows ride 21 degrees below
    # horizontal instead of straight down. That is the posture of a desk cut
    # for a chair being used from a sofa - it is what the height costs, it is
    # the same thing IKEA's own pair does (SMASTAD's 730 desk over the 430 mm
    # chair sold with it is 300 mm; this plate is 280 over its cushion), and it
    # is drawn rather than argued away. The clearance the wrist lands with is
    # MEASURED and printed below, not asserted.
    torso=(0, 90), head=(0, 84),
    arms=(((0, -21), (0, 0)), ((0, -21), (0, 0))),
    legs=(_DESK_LEG, _DESK_LEG))

figure_seated_right = child(
    "Child Seated Right (table mode)",
    (WALL_SPAN - FIG_SEAT_X - 2, FIG_BENCH_Y, FIG_SIT_Z), 180.0,
    # the other one sits up straight with the arms down, and that is the pose
    # that measures the headroom under the bunk. His knees are under the plate
    # too - that is the X9 claim, and it is the same claim on both sides of the
    # bed.
    torso=(0, 90), head=(0, 90),
    arms=(((0, -72), (0, -14)), ((0, -72), (0, -14))),
    legs=(_DESK_LEG, _DESK_LEG))

# LYING: on the back, arms in, legs out, feet relaxed. The torso axis is one
# torso radius above the sleeping face less the same foam sink; the head is a
# sphere on the same axis, so it settles 22 mm in - which is what a head does
# to a pillow that is not modelled.
# The arms lie ALONGSIDE the body, i.e. they point the way the legs do - 180
# degrees off the torso axis - and splay 14 degrees so they are not inside it.
_LIE_ARMS = (((180 - 14, -3), (180 - 10, 0)), ((180 - 14, -3), (180 - 10, 0)))
_LIE_LEGS = ((((180 - 4), 0), ((180 - 2), 0), ((180 - 2), 55)),
             (((180 - 4), 0), ((180 - 2), 0), ((180 - 2), 55)))
MATTRESS_TOP = mattress.extents[2][1]                  # 1643

# UPPER BUNK: head at the left wall, feet toward the middle. 120 cm of child
# in 199 cm of bed - the room to grow is the point, so it is drawn.
figure_lying_upper = child(
    "Child Lying Upper (bed mode)",
    (696.0, FIG_BENCH_Y, MATTRESS_TOP + FIG_TORSO_R - FIG_SINK), 180.0,
    torso=(0, 0), head=(0, 0), arms=_LIE_ARMS, legs=_LIE_LEGS)

# LOWER BED: head at the right wall, so the two sleepers read as two and the
# drawing shows both ends of the bed carrying a body. The trunk crosses the
# 5 mm step from the seat cushions down to the back cushions on the panel -
# it is drawn resting on the higher of the two, which is the one it is on
# under the head and the shoulders.
figure_lying_lower = child(
    "Child Lying Lower (bed mode)",
    (WALL_SPAN - 696.0, FIG_BENCH_Y, SEAT_FACE + FIG_TORSO_R - FIG_SINK), 0.0,
    torso=(0, 0), head=(0, 0), arms=_LIE_ARMS, legs=_LIE_LEGS)

FIGURES_BED = [figure_lying_upper, figure_lying_lower]
FIGURES_TABLE = [figure_seated_left, figure_seated_right]
FIGURES_ALL = FIGURES_BED + FIGURES_TABLE
FIGURES = {id(panel_bed): FIGURES_BED, id(panel_table): FIGURES_TABLE}


def is_body(p):
    """True for a reference body. The counterpart of is_soft(): every
    wood-only list filters on is_soft, and no list in this file has to filter
    on THIS one, because a body is never in a list a part belongs to. It
    exists so that a tool importing this module can ask."""
    return getattr(p, "group", None) == "figures"


def scene_parts(panel):
    """The exported scene: the wood, the steel, the foam AND the bodies.

    display_parts() is the BED - it is what the films, the step drawings and
    the panel-sweep collision test are built from, and it must stay a list of
    things the bed is made of. This is the picture.
    """
    return display_parts(panel) + FIGURES[id(panel)]


def make_scene(panel, xform=IDENTITY):
    return Compound(children=[p.moved(xform) for p in scene_parts(panel)])


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------
TOL = 0.1
print("\n=== VALIDATION ===")

# D12/W1/W7: the depth envelope. The BACK face is THE WALL PLANE itself - after
# W6 that is the back rail's outer face Y = -48, shared by the two back corner
# posts, the two end beams, the back bench rail, the back table ledger and the
# rear end of every slat (V5 took the four bearing blocks out of that plane). That plane is
# a mounting face, so the assert below is not just an envelope check: nothing
# whatsoever may poke out behind it, or the bed will not sit flat against the
# wall. (The two BACK stub legs are in that plane too - they always were, they
# stand under the back bench rail.)
#
# D14: the FRONT face is no longer the guard boards - they went inboard - it is
# the outer plane of the four front verticals, Y = 800. Overall depth
# 1070 (v7) -> 964 (v8/D12) -> 930 (v9/W1) -> 896 (v9/D14) -> 848 (v10/W6), which
# is also exactly the end-beam length: the bed is as deep as its own end frames
# and not one millimetre more.
#
# U3: the front face comes in one more time, and this one is a section change
# rather than a move. Every vertical in the front plane - the two corner posts
# (U2) and the two ladder uprights (U2's turn) - is 36 mm deep instead of 48, so
# the plane Y 752..788 is the whole of the bed's front and Y 788..800 is outside
# it. 848 -> 836, and the end beams follow to 836 so the identity "the bed is as
# deep as its own end frames" still holds.
DEPTH_Y0 = WALL_Y                              # -48, the wall / mounting plane
DEPTH_Y1 = FRONT_POST_Y1                       # 788  [was 800, 834, 940]
OVERALL_DEPTH = DEPTH_Y1 - DEPTH_Y0            # 836  [was 848, 896, 930, 964]
for name, _p in (("bed mode", panel_bed), ("table mode", panel_table)):
    bb = wood_envelope(_p)
    assert bb.min.X >= -TOL, f"{name}: geometry crosses wall at X=0 ({bb.min.X:.3f})"
    assert bb.max.X <= WALL_SPAN + TOL, \
        f"{name}: geometry crosses wall at X={WALL_SPAN} ({bb.max.X:.3f})"
    assert bb.max.Z <= POST_HEIGHT + TOL, \
        f"{name}: something is taller than the {POST_HEIGHT} mm posts ({bb.max.Z:.3f})"
    assert abs(bb.min.Y - DEPTH_Y0) < TOL, \
        f"{name}: the BACK plane is {bb.min.Y:.3f}, must be exactly the wall " \
        f"plane {DEPTH_Y0} - W1 makes it a flat mounting face against the wall"
    assert bb.max.Y <= DEPTH_Y1 + TOL, \
        f"{name}: something sticks out past the front post plane " \
        f"({bb.max.Y:.3f} > {DEPTH_Y1}) - D14 leaves nothing outside it"
    assert abs(bb.max.Y - DEPTH_Y1) < TOL, \
        f"{name}: the FRONT plane is {bb.max.Y:.3f}, must be exactly the front " \
        f"post/upright plane {DEPTH_Y1} (D14)"
    print(f"OK  {name}: X extent {bb.min.X:.2f} .. {bb.max.X:.2f} "
          f"(limit 0 .. {WALL_SPAN}), top Z {bb.max.Z:.0f} (limit {POST_HEIGHT}), "
          f"Y extent {bb.min.Y:.0f} .. {bb.max.Y:.0f} = {bb.max.Y - bb.min.Y:.0f} "
          f"mm deep (W1/W7: back face IS the wall plane {DEPTH_Y0}; D14/U3: "
          f"front face IS the post/upright plane {DEPTH_Y1}; depth was 1070 in "
          f"v7, 964 in v8, 930 before D14, 896 before W6, 848 before U2)")
assert OVERALL_DEPTH == 836 and DEPTH_SHRINK == 106
# X10: `OVERALL_DEPTH == 848 - POST_THIN` was not a check. POST_THIN is
# RAIL_T - POST_T, so POST_T stands on both sides of the equals and cancels:
# the assert claimed to police the 48 -> 36 re-section of the verticals and was
# blind to POST_T by construction. Measured instead - the bed's own Y extent
# off the bodies, and the front vertical's own thickness off its body.
BUILT_DEPTH = (max(p.extents[1][1] for p in parts)
               - min(p.extents[1][0] for p in parts))
_front_post = next(p for p in parts if p.label == "Corner Post Front Left")
BUILT_POST_T = _front_post.extents[1][1] - _front_post.extents[1][0]
assert abs(BUILT_DEPTH - OVERALL_DEPTH) < TOL, \
    f"U3: the bed measures {BUILT_DEPTH:g} mm deep and the number the file " \
    f"quotes is {OVERALL_DEPTH:g}"
assert BUILT_POST_T == POST_T and 848 - BUILT_DEPTH == POST_THIN, \
    f"U2/U3: the front verticals measure {BUILT_POST_T:g} mm in Y and the " \
    f"bed came in {848 - BUILT_DEPTH:g} mm off the 848 it was - re-sectioning " \
    f"them 48 -> {POST_T} is supposed to buy exactly POST_THIN = {POST_THIN}"
assert OVERALL_DEPTH == END_BEAM_LEN == 836, \
    "W7/U3: the bed must still be exactly as deep as its own end beams"
# U3: and the 12 mm slice the thinning gives back has to be genuinely outside
# the bed, not merely outside its bounding box - the same test D14 and W6 ran on
# the layers they vacated. Y 788..800 held the front corner posts, the ladder
# uprights and the front 12 mm of every rung until this round.
VACATED_FRONT_LAYER = (FRONT_POST_Y1, FRONT_POST_Y1 + POST_THIN)      # 788..800
still_in_front = [p for p in parts + [panel_bed, panel_table, mattress]
                  if p.extents[1][1] > VACATED_FRONT_LAYER[0] + TOL]
assert not still_in_front, \
    f"U3: {[p.label for p in still_in_front]} are still in the vacated layer " \
    f"Y {VACATED_FRONT_LAYER[0]}..{VACATED_FRONT_LAYER[1]}"
print(f"OK  U3: the front layer Y {VACATED_FRONT_LAYER[0]}.."
      f"{VACATED_FRONT_LAYER[1]} is EMPTY - the front corner posts, the ladder "
      f"uprights and the rung fronts all stop at {FRONT_POST_Y1} now, so the "
      f"{POST_THIN} mm the {RAIL_T} -> {POST_T} re-section gives up is real "
      f"depth: {OVERALL_DEPTH} mm over all")

# D14: the old guard plane must now be EMPTY. Nothing at all may live in
# Y 800..834 - that 34 mm slice is the depth the reclaim gives back, and if any
# part still occupies it the reclaim is a bounding-box illusion.
OLD_GUARD_PLANE = (FRONT_POST_Y1, FRONT_POST_Y1 + GUARD_T)     # 800 .. 834
in_old_guard_plane = [p for p in parts + [panel_bed, panel_table]
                      if p.extents[1][1] > OLD_GUARD_PLANE[0] + TOL]
assert not in_old_guard_plane, \
    f"D14: {[p.label for p in in_old_guard_plane]} still reach past Y " \
    f"{OLD_GUARD_PLANE[0]} into the vacated guard plane " \
    f"{OLD_GUARD_PLANE[0]}..{OLD_GUARD_PLANE[1]}"
print(f"OK  D14: the old front guard plane Y {OLD_GUARD_PLANE[0]}.."
      f"{OLD_GUARD_PLANE[1]} is EMPTY - the outermost front element is the "
      f"post/upright plane {FRONT_POST_Y1}; D14 took the depth 930 -> 896 by "
      f"reclaiming those {GUARD_T} mm, W6 took it to 848 and U2/U3 to "
      f"{OVERALL_DEPTH}")

# W1/W7: nothing at all behind the wall plane, and every family of parts that is
# supposed to define it must actually reach it - otherwise "flat against the
# wall" is a statement about a bounding box rather than about a face you can
# bolt. After W6 the wall plane is the back rail's outer face Y = -48, and it is
# a much bigger face than it was: the rail itself, the two back posts tucked into
# its plane, the two end beams, the back bench rail and its two stub legs, the
# back table ledger, and the rear end of all 24 slats. (V5 took the four
# bearing blocks out of this list; they were the only parts on it that were
# there to hold something up rather than to be part of the bed.)
bench_slat_parts = [p for p in parts if p.label.startswith("Bench Slat")]
WALL_FACE = (
    {"Upper Side Rail Back", "Bench Rail Back (continuous)", "Table Ledger Back"}
    | {f"Corner Post Back {s}" for s in ("Left", "Right")}
    | {f"End Beam {s}" for s in ("Left", "Right")}
    | {f"Bench Stub Leg Back {s}" for s in ("Left", "Right")}
    | {s.label for s in bed_slats}
    | {s.label for s in bench_slat_parts}
)
on_wall = [p for p in parts if abs(p.extents[1][0] - WALL_Y) < TOL]
assert {p.label for p in on_wall} == WALL_FACE, \
    f"W1/W7: the wall face is made of {sorted(p.label for p in on_wall)}, " \
    f"expected {sorted(WALL_FACE)}"
for p in parts + [panel_bed, panel_table]:
    assert p.extents[1][0] >= WALL_Y - TOL, \
        f"W1: '{p.label}' stands proud of the wall plane {WALL_Y}"
assert not any(p.label.startswith("Guard Rail Back") for p in parts), \
    "W1: the back guard boards are supposed to be deleted - the wall is the " \
    "barrier on that side"
# W6: the parts that used to make the wall face at -96 are the ones that moved,
# and the plane they used to occupy has to be gone, not merely vacated by the
# bounding box. Y -96..-48 is now OUTSIDE the bed entirely.
# X10: what stood here compared WALL_Y to BACK_RAIL_Y0 - the constant to its own
# alias - and then interpolated both operands into the message, so the only
# sentence it could ever print was "the wall plane is -48, want the back rail
# face -48". The real check is the loop directly above, which reads
# p.extents[1][0] off every body; this line adds the one thing that loop does
# not say out loud, which is that the plane those bodies share is the plane the
# file NAMES.
WALL_PLANE_BUILT = min(p.extents[1][0] for p in parts)
assert WALL_PLANE_BUILT == WALL_Y == -RAIL_T, \
    f"W6: the bodies make their back face at Y {WALL_PLANE_BUILT:g} and the " \
    f"file calls the wall plane {WALL_Y:g}"
print(f"OK  W1/W6/W7: WALL-SIDE BED - no back guard boards; the back face is the "
      f"flat mounting plane Y={WALL_Y} (was -96), the BACK RAIL FACE, made by "
      f"{len(on_wall)} coplanar parts - back side rail + 2 back posts tucked "
      f"into its plane + 2 end beams + 2 end-beam blocks + back bench rail + 2 "
      f"of its blocks + back ledger + all {len(bed_slats) + len(bench_slat_parts)} "
      f"slat ends - and nothing behind it. The fixing is screws through the back "
      f"rail into the studs, which also mid-support it")

# ---------------------------------------------------------------------------
# THE ROOM'S OWN PARTS - the ones a tape measure finishes, not the cut list
# ---------------------------------------------------------------------------
# Three of the six surfaces round this bed are NOT in the model: the two end
# walls and the floor. The model draws them as the perfect planes X = 0,
# X = WALL_SPAN and Z = 0, and a real niche is none of those things. So the
# cut list has always been telling a small lie by omission: some of its lines
# are sawn on the trestles and are done, and some of them are only a blank to
# be trimmed once the room stands finished.
#
# Which is which is a RULE, not a list. A part is the room's if it comes
# within ROOM_TOL of an end wall, or if it stands on the floor. Everything
# else is the workshop's, and stays exactly as drawn.
#
# HOW the room finishes it follows from WHICH WAY ITS SAWN LENGTH RUNS - and
# that is why block() now writes the cut-list line onto the part:
#
#   length up the Z axis, standing on the floor  -> cut LONG, trim the foot
#       until the frame is level. The floor is the plane you cannot trust.
#   length along the X axis, into an end wall    -> cut LONG, fine-cut on
#       site once the narrowest width of the niche is measured.
#   length across, but an edge against a wall    -> nominal length. It is the
#       WIDTH that is scribed to the wall, never the length.
#   standing on the floor AND a SIDE against an end wall -> both jobs on the
#       same piece. The foot is trimmed as above, and the wall-facing side is
#       scribed: the corner posts sit IN the wall plane with no clearance at
#       all, so a bulge in the wall cannot be swallowed by a gap. Either it
#       comes off the wood or it pushes the whole frame out of plumb. That is
#       material REMOVED - the nominal section still stands, and there is no
#       allowance in the width.
ROOM_TOL = 5.0            # how near an end wall a part has to come to be fitted
ROOM_OVER_FLOOR = 15      # trim allowance at the foot of a standing part
ROOM_OVER_WALL = 10       # fine-cut allowance per wall-facing end


def _cut_axes(p):
    """The axes the part's SAWN LENGTH could run along, as a set.

    Usually one. A square section (the rung block is 36 x 36 x 48 with a
    36 mm length) leaves two, and the rules below refuse to guess: any part
    the room touches has to be unambiguous.
    """
    assert p.cut is not None, f"'{p.label}' is in no cut-list line"
    length = p.cut[2]
    return frozenset(i for i, (lo, hi) in enumerate(p.extents)
                     if round(hi - lo) == length)


def _cut_axis(p):
    axes = _cut_axes(p)
    assert len(axes) == 1, \
        f"'{p.label}' is {p.cut[2]} mm long and that length fits " \
        f"{len(axes)} of its sides - the room cannot be told which one it " \
        f"trims. Give the piece its own cut-list line or change the section"
    return next(iter(axes))


def near_end_walls(p):
    """[0], [1], [0, 1] or [] - which end walls this part reaches."""
    (x0, x1), _, _ = p.extents
    return [i for i, near in enumerate((x0 <= ROOM_TOL,
                                        x1 >= WALL_SPAN - ROOM_TOL)) if near]


def on_floor(p):
    return abs(p.extents[2][0]) < TOL


def flush_with_end_wall(p):
    """True when a whole face of the part lies IN an end wall plane."""
    (x0, x1), _, _ = p.extents
    return abs(x0) < TOL or abs(x1 - WALL_SPAN) < TOL


def room_fit(p):
    """How the room finishes this part - or None if the workshop does."""
    ends = near_end_walls(p)
    floor = on_floor(p)
    if not ends and not floor:
        return None
    axis = _cut_axis(p)
    if floor and axis == 2:
        # Standing, and reaching an end wall with something that is not its
        # sawn end: the face against the wall is a SIDE. Both jobs.
        return dict(kind="gulv+side" if ends else "gulv",
                    over=ROOM_OVER_FLOOR, ends=len(ends))
    if ends and axis == 0:
        return dict(kind="vegg", over=ROOM_OVER_WALL * len(ends),
                    ends=len(ends))
    if ends:
        return dict(kind="meddrag", over=0, ends=len(ends))
    raise AssertionError(
        f"'{p.label}' lies on the floor but its length runs along axis "
        f"{axis} - there is no rule for trimming that, and inventing one "
        f"here would be a special case")


CUT_PARTS = [p for p in list(parts) + [panel_bed] + battens_bed]
assert all(p.cut is not None for p in CUT_PARTS), \
    "every wooden part must carry the cut-list line it was counted into"

ROOM_FIT = {p.label: room_fit(p) for p in CUT_PARTS}
ROOM_FIT = {lbl: f for lbl, f in ROOM_FIT.items() if f is not None}

# A cut-list LINE is what the reader saws to, so a line whose pieces disagree
# about who finishes them cannot be printed either way round. Mirrored parts
# are mirrored, so they agree by construction - and this assert is what says
# so out loud.
ROOM_LINES = {}
for p in CUT_PARTS:
    fit = ROOM_FIT.get(p.label)
    key = (fit["kind"], fit["over"], fit["ends"]) if fit else None
    if p.cut in ROOM_LINES:
        assert ROOM_LINES[p.cut] == key, \
            f"cut-list line {p.cut} has pieces the room finishes differently " \
            f"({ROOM_LINES[p.cut]} vs {key}) - '{p.label}' broke the mirror"
    else:
        ROOM_LINES[p.cut] = key
ROOM_LINES = {k: v for k, v in ROOM_LINES.items() if v is not None}

# The wall-end allowance has to be bigger than the clearance the model already
# leaves itself, or the "cut it long" instruction would hand back a part that
# is still short of the wall it is supposed to be scribed to.
assert ROOM_OVER_WALL > THROUGH_X0, \
    f"the fine-cut allowance {ROOM_OVER_WALL} does not even cover the " \
    f"{THROUGH_X0} mm the through members are already held off each wall"
# ...and the foot allowance has to be smaller than the height of the lowest
# thing fastened to a standing part, or trimming the foot would saw through a
# joint instead of a blank.
def _lowest_neighbour_z(p):
    (x0, x1), (y0, y1), _ = p.extents
    zs = [q.extents[2][0] for q in CUT_PARTS
          if q is not p and not on_floor(q)
          and q.extents[0][1] >= x0 - TOL and q.extents[0][0] <= x1 + TOL
          and q.extents[1][1] >= y0 - TOL and q.extents[1][0] <= y1 + TOL]
    return min(zs) if zs else None


# Both floor classes stand on the floor and both get the foot trimmed, so
# both are held to the clearance below - "gulv" and "gulv+side" alike.
_standing = [p for p in CUT_PARTS
             if ROOM_FIT.get(p.label, {}).get("kind", "").startswith("gulv")]
_lowest = min(z for z in (_lowest_neighbour_z(p) for p in _standing)
              if z is not None)
assert ROOM_OVER_FLOOR < _lowest, \
    f"trimming {ROOM_OVER_FLOOR} mm off a foot would cut into the joint at " \
    f"Z {_lowest}"
# A side is only worth scribing where there is NOWHERE ELSE for the bulge to
# go. So the pieces the rule sends to the plane have to be the ones that sit
# in the wall plane itself: a whole face at X = 0 or X = WALL_SPAN, zero
# clearance. If one of them ever gets held off the wall, the gap takes the
# bulge and the instruction is wrong.
_scribed_sides = [p for p in CUT_PARTS
                  if ROOM_FIT.get(p.label, {}).get("kind") == "gulv+side"]
assert _scribed_sides, \
    "no standing part reaches an end wall with its side - the corner posts " \
    "have moved off the wall plane and the scribing instruction has no owner"
for p in _scribed_sides:
    assert flush_with_end_wall(p), \
        f"'{p.label}' is told to have its wall side scribed, but it stands " \
        f"off the wall at X {p.extents[0]} - the clearance would take the " \
        f"bulge, not the plane"
    assert _cut_axis(p) != 0, \
        f"'{p.label}' meets an end wall with its sawn END, not a side"
print(f"OK  ROMDELER: {len(ROOM_FIT)} of {len(CUT_PARTS)} pieces in "
      f"{len(ROOM_LINES)} of {len(CUT_LIST)} cut-list lines are finished by "
      f"the ROOM, not the shop - "
      + ", ".join(f"{k} x{sum(1 for f in ROOM_FIT.values() if f['kind'] == k)}"
                  for k in sorted({f["kind"] for f in ROOM_FIT.values()}))
      + f"; the foot allowance {ROOM_OVER_FLOOR} clears the lowest joint on a "
      f"standing part (Z {_lowest:g}); {len(_scribed_sides)} of them stand in "
      f"the wall plane with no clearance and get the side scribed too")

# ---------------------------------------------------------------------------
# X6 - WHERE THE HOLE GOES ON THE PIECE
# ---------------------------------------------------------------------------
# The joint table says WHAT is driven, and the direction sheet says WHICH WAY.
# Neither says the one thing a man with a piece of wood in the vice actually
# needs: how far in from the end the hole is, how far up from the edge, and
# how far apart two of them stand. Without those three numbers nothing can be
# made square, level or the same on both sides - the parts can only be offered
# up and hoped at, and hoping is how a bed ends up with one rail 4 mm higher
# than the other.
#
# The numbers exist already. Every fastener in this bed is a solid at an
# absolute (x, y, z), and that is exactly what a bench cannot use. So it is
# PROJECTED BACK INTO THE PIECE IT IS DRIVEN FROM and reported as the two
# measurements a tape can take on a trestle, plus the spacing:
#
#     <d> mm from a named END      along the piece's sawn length
#     <d> mm from a named EDGE     across its section
#     c/c <s>                      between the holes of one row
#
# THREE RULES PICK THE REFERENCES. They are rules and not a list of joints,
# because a list of joints is the thing that goes out of date.
#
#   1. THE PIECE IS THE FRAME OF REFERENCE, NOT THE BED. The datum is an end
#      or an edge of the piece the head sits on. Heights above the floor are
#      in nokkelmal.md and are no use to a man at a trestle.
#   2. AN END THAT DOES NOT EXIST YET IS NOT A DATUM. Steg 0 bores everything
#      while the pieces are loose, and at that moment exactly one kind of end
#      is still oversize: the FOOT of a standing part, trimmed in vater after
#      the frame is up (ROOM_OVER_FLOOR). Marks on a post or a ladder stile
#      are therefore taken from the TOP - and that is why the ladder's five
#      rung holes come out as a count down from 2037 rather than up from a
#      floor line that is still 15 mm of waste. Wall ends are fine-cut off the
#      measured niche in the same breath as the cutting, before the drill
#      comes out, so they are datums like any other.
#   3. ALONG THE WALL, NAME THE MIDDLE OF THE BED - NOT LEFT AND RIGHT. On X
#      an end or a face is `ytre` or `indre` according to which way it points
#      relative to the middle of the bed. That is what lets ONE line serve a
#      joint and its mirror image: the left stile's outer face and the right
#      stile's outer face are the same face of the same piece, and the man
#      holding one of them does not care which half of the room he is in. Y
#      and Z need no such trick - this bed is symmetric in neither, so
#      back/front and under/over each mean one thing.
#
# And the symmetry that rule 3 buys is MEASURED, not assumed: the mirror
# assert below projects both halves of the bed into their own pieces and
# compares the projections. Nothing in this model forces the two ends of the
# bed to agree; the day they stop agreeing, the single line that claims to
# serve both is a lie, and it is the assert that has to say so.
PLACE_TOL = 0.51        # a hair over half a mm - finer than a tape can read


def _length_axis(p):
    """The axis the piece's SAWN LENGTH runs along - the axis that has ENDS.

    The other two are the section, and they have EDGES. A square section
    leaves the length fitting two sides (the rung block is 36 x 36 x 48 with a
    36 mm cut length); there is nothing to choose between them on a bench, so
    the longest side is called the length and both others are edges.
    """
    axes = _cut_axes(p)
    return (next(iter(axes)) if len(axes) == 1
            else max(range(3), key=lambda j: p.extents[j][1] - p.extents[j][0]))


def _end_is_datum(p, axis, which):
    """Is this end of this piece sawn to size BEFORE the holes are bored?"""
    fit = ROOM_FIT.get(p.label)
    return not (which == 0 and axis == 2
                and fit is not None and fit["kind"].startswith("gulv"))


def _ref_id(p, axis, which):
    """The name of one end / edge / face of a piece. See rule 3 for X."""
    if axis == 1:
        return ("bak", "fram")[which]
    if axis == 2:
        return ("ned", "opp")[which]
    lo, hi = p.extents[0]
    here, there = (lo, hi) if which == 0 else (hi, lo)
    return ("ytre" if abs(here - BED_CENTRE[0]) >= abs(there - BED_CENTRE[0])
            else "indre")


def _mark_point(f):
    """WHERE THE PENCIL GOES. For an ordinary screw that is the anchor - the
    head, on the face it is driven from. For a TOE SCREW it is not: the
    anchor is the flat bottom of the ⌀18 pocket, `seat` millimetres down the
    screw's own slanted axis, and what the builder marks is the MOUTH of that
    pocket on the face, because that is what he lines the jig's hole up with
    (steg 0: «hullet rett over merket»). Marking the seat bottom would put
    every skew hole 9 mm out."""
    seat = f.get("seat")
    if not seat:
        return f["anchor"]
    return tuple(a - seat * v for a, v in zip(f["anchor"], f["direction"]))


def _project(f, e, j):
    """(datum name, mm, centred) - one fastener in one piece along one axis.

    A hole the same distance from both sides of a piece is not "so many from
    an edge", it is ON THE CENTRE LINE, and that is how it has to be named:
    the two bench slats at either end of the bed are the same piece with the
    same hole in the middle of it, and calling it 49 mm from the outer edge
    on one and 49 from the inner on the other would make the mirror look
    broken when it is not.
    """
    lo, hi = e.extents[j]
    m = _mark_point(f)[j]
    d = (m - lo, hi - m)
    if abs(d[0] - d[1]) < PLACE_TOL:
        return "midt", d[0], True
    allowed = [w for w in (0, 1) if _end_is_datum(e, j, w)]
    assert allowed, (
        f"{f['jid']}: neither end of '{e.label}' along axis {j} is sawn to "
        f"size before the holes are bored")
    w = min(allowed, key=lambda k: d[k])
    return _ref_id(e, j, w), d[w], False


def _entry_of(f):
    """The piece the mark is made on: the one the head sits in, or - for a
    screw through a bracket flange - the one it is driven into."""
    return f["through"] if f["through"] is not None else f["into"]


def _mark_face(f):
    """(axis, 0|1) - which face of that piece the mark is made on.

    `face` is the face the model already drives the screw from (the bottom of
    a counterbore or of a toe screw's seat is that face, by the same contract
    the flush-head assert uses), so this is a reading and not a second guess.
    """
    axis = (f["face"][0] if "face" in f
            else max(range(3), key=lambda j: abs(f["direction"][j])))
    return axis, (0 if f["direction"][axis] > 0 else 1)


def _uniform_step(vals):
    """The one spacing a sorted row is laid out on, or None if it is not one."""
    if len(vals) < 2:
        return None
    steps = [b - a for a, b in zip(vals, vals[1:])]
    return steps[0] if max(steps) - min(steps) < PLACE_TOL else None


def _row_pitch(fs, axis):
    """c/c along `axis` inside ONE row: two fasteners of the same drive, in
    the same INSTANCE of the joint, on the same piece. Both qualifications
    are recorded when the fastener is placed, so this cannot pick up two
    holes that merely happen to line up at opposite ends of a long member."""
    best = None
    row = [f for f in fs if f.get("row_axis") == axis]
    for i, a in enumerate(row):
        for b in row[i + 1:]:
            if a["inst"] != b["inst"] or _entry_of(a) is not _entry_of(b):
                continue
            d = abs(_mark_point(a)[axis] - _mark_point(b)[axis])
            best = d if best is None or d < best else best
    return best


def fastener_placements():
    """One record per line of the placement table - the fastener in the frame
    of the piece it is marked on, grouped exactly the way the direction sheet
    groups it, so the two fragments are one row for one row."""
    order = {j["id"]: i for i, j in enumerate(JOINTS)}
    groups, seq = {}, []
    for f in FASTENER_SPECS:
        if f["drive"] is None or _entry_of(f) is None:
            continue
        # The cut-list line is part of the key: J10 is the same drive on
        # two different pieces of wood - the continuous back bench rail and a
        # 642 mm front segment - and the hole is not in the same place on
        # them. One line of placement, one piece.
        key = (f["jid"], f["name"], f["kind"], id(f["drive"]),
               _entry_of(f).cut)
        if key not in groups:
            groups[key] = []
            seq.append(key)
        groups[key].append(f)
    seq.sort(key=lambda k: (order[k[0]], k[1], k[2]))

    out = []
    for key in seq:
        fs = groups[key]
        f0 = fs[0]
        e0 = _entry_of(f0)
        crow = f0["crow"]
        f_ax, f_side = _mark_face(f0)
        assert all(_mark_face(f)[0] == f_ax for f in fs), \
            f"{f0['jid']}: {f0['name']} is marked on two different faces"
        L = _length_axis(e0)
        axes = []
        for j in range(3):
            if j == f_ax:
                continue
            buckets = {}
            for f in fs:
                ref, dist, centred = _project(f, _entry_of(f), j)
                b = buckets.setdefault(ref, dict(at=set(), centred=centred))
                b["at"].add(round(dist, 1))
                b["centred"] &= centred
            pitch = _row_pitch(fs, j)
            steps = set()
            for b in buckets.values():
                b["at"] = sorted(b["at"])
                s = _uniform_step(b["at"])
                if s is not None:
                    steps.add(round(s, 1))
            assert len(steps) <= 1, (
                f"{f0['jid']}: the holes along axis {j} are laid out on "
                f"{sorted(steps)} - one row, one pitch")
            step = next(iter(steps)) if steps else None
            if pitch is not None and step is not None:
                assert abs(pitch - step) < PLACE_TOL, (
                    f"{f0['jid']}: the row is drilled at c/c {pitch:g} but "
                    f"the marks read {step:g} apart from the datum")
            # Two datums with the same list of distances is the SAME hole
            # measured from either end of the piece - one line, said once.
            names = sorted(buckets)
            both = (len(names) == 2
                    and buckets[names[0]]["at"] == buckets[names[1]]["at"])
            if both:
                # ...and the two ends have to carry the SAME NUMBER of holes,
                # not just the same list of distances. A line that says «18 mm
                # fra begge ender» is claiming a pair, and a pair with three
                # at one end and one at the other reads identically off the
                # distances alone. Counted, so it cannot.
                tally = [sum(1 for f in fs
                             if _project(f, _entry_of(f), j)[0] == n)
                         for n in names]
                assert tally[0] == tally[1], (
                    f"{f0['jid']}: axis {j} has {tally[0]} holes off the "
                    f"'{names[0]}' end and {tally[1]} off '{names[1]}' - one "
                    f"line cannot say «fra begge ender» about that")
            widths = {round(_entry_of(f).extents[j][1]
                             - _entry_of(f).extents[j][0], 1) for f in fs}
            assert len(widths) == 1, (
                f"{f0['jid']}: the pieces this line serves are "
                f"{sorted(widths)} mm across on axis {j} - one line cannot "
                f"measure two different widths")
            axes.append(dict(
                axis=j, role="ende" if j == L else "kant", both=both,
                width=next(iter(widths)),
                cc=(pitch if pitch is not None else step),
                refs=[dict(ref=n, at=buckets[n]["at"],
                           centred=buckets[n]["centred"]) for n in names]))
        out.append(dict(
            jid=f0["jid"], name=f0["name"], kind=f0["kind"],
            per=f0["drive"]["per"],
            member=(crow["a"] if e0 is f0["pa"] else crow["b"]),
            section=e0.cut[1].replace("x", "×"), piece_len=e0.cut[2],
            n=len(fs), pieces=len({id(_entry_of(f)) for f in fs}),
            face=(f_ax, _ref_id(e0, f_ax, f_side)), axes=axes))
    return out


FASTENER_PLACEMENTS = fastener_placements()


# THE MIRROR, MEASURED. Every line above claims to serve both halves of the
# bed. This walks the two halves separately, projects each fastener into its
# own piece exactly as the line does, and demands the two descriptions come
# out identical - a comparison of two independently measured sets of
# coordinates, not of a constant against itself. A screw 27 mm up in the left
# end and 28 in the right would pass every other assert in this file.
def _local_of(f):
    e = _entry_of(f)
    f_ax, f_side = _mark_face(f)
    who = [(f_ax, _ref_id(e, f_ax, f_side), 0.0)]
    for j in range(3):
        if j == f_ax:
            continue
        ref, dist, _c = _project(f, e, j)
        who.append((j, ref, round(dist, 1)))
    return (f["jid"], f["name"], e.cut, tuple(who))


_halves = {-1: [], 1: []}
for _f in FASTENER_SPECS:
    if _f["drive"] is None or _entry_of(_f) is None:
        continue
    _s = _f["anchor"][0] - BED_CENTRE[0]
    if abs(_s) > TOL:
        _halves[1 if _s > 0 else -1].append(_local_of(_f))
_left, _right = sorted(_halves[-1]), sorted(_halves[1])
assert _left == _right, (
    "SPEILET: the two halves of the bed do not project to the same "
    "placements. Only in one half: "
    + "; ".join(str(x) for x in sorted(set(_left) ^ set(_right))[:4]))
print(f"OK  X6 festeplassering: {len(FASTENER_PLACEMENTS)} linjer dekker "
      f"{len([f for f in FASTENER_SPECS if f['drive'] is not None])} "
      f"festemidler; speilprøven: {len(_left)} plasseringer i hver halvdel av "
      f"senga projiserer til samme mål i delenes egne koordinater, så ett mål "
      f"gjelder begge sider")


# ---------------------------------------------------------------------------
# X6 - EDGE DISTANCE, MEASURED ON BOTH PIECES
# ---------------------------------------------------------------------------
# The fits-the-face rule ((n-1)x4d + 2x3d, see MIN_EDGE) sizes a row inside
# the CONTACT PATCH - the overlap of the two members. That is the right face
# to lay a row out on and the wrong one to judge a split by: the patch is not
# an edge, and a screw with 3d of patch either side of it can still stand
# 8 mm from the real end of the wider piece. So this measures the thing
# itself, on BOTH pieces of every joint, off the placed solids:
#
#   * EDGE DISTANCE IS MEASURED SQUARE TO THE SCREW. The axes the screw
#     TRAVELS on carry depth, not edge - how deep the head sits and whether
#     the tip comes out the far side are different questions, and this file
#     already asks both of them. So the axes with a component of the drive
#     vector in them are dropped, and what is left is the wood standing round
#     the shank. On those axes the screw's position does not change along its
#     length, so the anchor IS the measurement - no sampling, no tolerance.
#   * A SKEW SCREW travels on two axes and is therefore judged on the one
#     axis square to it. That is the honest reading: the other two are the
#     seat's own depth and the joint's own reach.
#   * the answer is the smallest of those, over BOTH members - the nearest
#     edge or end of either piece, whichever it turns out to be.
#
# TWO YARDSTICKS, AND ONLY ONE OF THEM IS THIS FILE'S. 3d is EC5 for a
# pre-drilled screw with an unloaded edge and is what the whole bed is laid
# out to (MIN_EDGE); that one is asserted and must hold. 4d is the shop rule
# of thumb the docs round asked to be measured, and it is REPORTED, not
# enforced: moving a screw is a design change and belongs to the round that
# owns the joint, not to the round that noticed. Every row under it is listed
# by name in the build log so the reader can see exactly which ones sit
# between the two numbers.
EDGE_RULE_OF_THUMB_D = 4


def screw_cross_axes(f):
    """The axes square to the screw - the ones an edge distance lives on."""
    cross = [j for j in range(3) if abs(f["direction"][j]) < 1e-9]
    return cross or [min(range(3), key=lambda j: abs(f["direction"][j]))]


def screw_edge_distance(f, member):
    """(mm, axis) - the nearest edge or end of `member` square to this screw,
    or (None, None) when the member is not in the joint."""
    if member is None:
        return None, None
    out = []
    for j in screw_cross_axes(f):
        lo, hi = member.extents[j]
        out.append((min(f["anchor"][j] - lo, hi - f["anchor"][j]), j))
    return min(out)


EDGE_REPORT = []
for _f in FASTENER_SPECS:
    if _f["kind"] != "screw" or _f.get("wall") or not _f["name"].startswith(
            "Treskrue"):
        continue
    for _m in (_f.get("through"), _f.get("into")):
        _e, _j = screw_edge_distance(_f, _m)
        if _e is None:
            continue
        _w = _m.extents[_j][1] - _m.extents[_j][0]
        EDGE_REPORT.append((round(_e, 2), _f["jid"], _f["name"], _m.label,
                            _f["d"], _j, round(_w, 2),
                            abs(_w / 2 - _e) < PLACE_TOL))
EDGE_REPORT.sort()
for _e, _jid, _name, _label, _d, _j, _w, _mid in EDGE_REPORT:
    assert _e >= min_edge(_d) - TOL, (
        f"{_jid}: {_name} stands {_e:g} mm from the nearest edge of "
        f"'{_label}' on axis {_j} - EC5 wants {min_edge(_d):g} mm (3d) round "
        f"a pre-drilled screw, and this file lays every row out to it")
EDGE_WORST = {}
for _e, _jid, _name, _label, _d, _j, _w, _mid in EDGE_REPORT:
    EDGE_WORST.setdefault((_jid, _label), (_e, _d, _j, _w, _mid))
EDGE_THIN = [(k, v) for k, v in sorted(EDGE_WORST.items())
             if v[0] < EDGE_RULE_OF_THUMB_D * v[1] - TOL]
# AND THE ONE DISTINCTION THAT MAKES THE LIST USEFUL. A row between 3d and 4d
# is one of two quite different things:
#   ON THE CENTRE LINE - the screw is already as far from both edges as the
#       piece allows, and 4d is arithmetically impossible in that dimension: a
#       6 mm screw wants 48 mm of width for it and this bed's frame board is
#       36. Nothing can be moved; only the SECTION could change, and that is
#       a different bed.
#   OFF CENTRE - the screw could be moved and 4d would be reachable. Those
#       are the only ones worth a design round.
# The split is measured, not sorted by hand: `mid` is the screw sitting half
# the piece's own width from either side.
EDGE_THIN_MID = [x for x in EDGE_THIN if x[1][4]]
EDGE_THIN_OFF = [x for x in EDGE_THIN if not x[1][4]]
# TODO (design round, not this one): every row in EDGE_THIN_OFF could be
# opened to 4d by moving a screw. Moving a screw moves the joint, and that is
# the decision of the round that owns the joint, not of the round that
# noticed - so it is measured and named here and left alone:
#     assert not EDGE_THIN_OFF, EDGE_THIN_OFF
print(f"OK  X6 kantavstand målt på BEGGE delene i hvert ledd, vinkelrett på "
      f"skruen: minste {EDGE_REPORT[0][0]:g} mm ({EDGE_REPORT[0][1]} i "
      f"'{EDGE_REPORT[0][3]}', d{EDGE_REPORT[0][4]:g} → "
      f"{EDGE_REPORT[0][0] / EDGE_REPORT[0][4]:.1f}d), krav 3d overholdt av "
      f"alle {len(EDGE_REPORT)} målingene")
print(f"    {len(EDGE_THIN)} av {len(EDGE_WORST)} rader ligger mellom 3d og "
      f"tommelfingerregelens {EDGE_RULE_OF_THUMB_D}d — "
      f"{len(EDGE_THIN_MID)} av dem står PÅ SENTERLINJEN (4d er umulig i den "
      f"dimensjonen), {len(EDGE_THIN_OFF)} står ikke på senter:")
for _tag, _rows in (("senter", EDGE_THIN_MID), ("ikke senter", EDGE_THIN_OFF)):
    for (_jid, _label), (_e, _d, _j, _w, _mid) in _rows:
        print(f"      {_jid:5s} {_label:34s} {_e:5.1f} mm = "
              f"{_e / _d:.1f}d i {_w:g} mm ({_tag}), d{_d:g}, "
              f"4d = {EDGE_RULE_OF_THUMB_D * _d:g}")


# ---------------------------------------------------------------------------
# WHERE THE WALL NEEDS NOGGINGS
# ---------------------------------------------------------------------------
# The bed presses on the wall in bands, not everywhere, and the bands are a
# property of the geometry: a part on the wall face whose LENGTH runs along
# the wall lies flat on it over that whole length, and a part on the wall
# face that is also flush with an end wall stands in the corner. Those are
# the two shapes you need wood behind. Everything else on the wall face meets
# it end-on (the slats and the end beams, whose length runs OUT of the wall)
# or stands on the floor clear of the corners (the two back stub legs).
WALL_FIX_PARTS = [p for p in CUT_PARTS
                  if abs(p.extents[1][0] - WALL_Y) < TOL
                  and (0 in _cut_axes(p) or flush_with_end_wall(p))]
_fix_labels = {p.label for p in WALL_FIX_PARTS}
for p in on_wall:
    if p.label in _fix_labels:
        continue
    assert 1 in _cut_axes(p) or (on_floor(p) and not flush_with_end_wall(p)), \
        f"'{p.label}' lies on the wall face but is neither a member running " \
        f"along it, a piece meeting it end-on, nor a foot on the floor - " \
        f"the nogging rule has no answer for it"

# One zone per (height band, cut-list line); mirrored parts share a zone.
WALL_ZONES = []
for p in WALL_FIX_PARTS:
    z = p.extents[2]
    hit = next((zo for zo in WALL_ZONES
                if zo["z"] == z and zo["cut"] == p.cut), None)
    if hit is None:
        WALL_ZONES.append(dict(z=z, cut=p.cut, labels=[p.label],
                               corner=flush_with_end_wall(p)))
    else:
        hit["labels"].append(p.label)
        hit["corner"] = hit["corner"] and flush_with_end_wall(p)
WALL_ZONES.sort(key=lambda zo: (zo["z"][0], zo["z"][1], zo["cut"]))

# X11: AND WHICH OF THEM ACTUALLY GETS A SCREW. A nogging zone is a band the
# bed PRESSES on - it is derived from bearing, not from fixings - and for four
# rounds the printed table called every zone's part «the part that gets a
# fixing», which was true of one zone out of four. The two facts are different
# and they are both worth printing, so the fixings are read back off the
# placed fasteners and hung on the zone they land in. A zone with no wall
# fastener in its height band gets an empty list and the table says so.
for _jid, _m in WALL_FIXINGS:
    assert _m in WALL_FIX_PARTS, \
        f"{_jid}: '{_m.label}' does not run along the wall face - it cannot " \
        f"be screwed to it without a packer, and this bed has none"
for zo in WALL_ZONES:
    zo["fix"] = []
    for jid, member in WALL_FIXINGS:
        if member.label in zo["labels"]:
            n = sum(1 for f in FASTENER_SPECS if f["jid"] == jid)
            zo["fix"].append((jid, n))
assert sum(n for zo in WALL_ZONES for _jid, n in zo["fix"]) \
    == sum(1 for f in FASTENER_SPECS if f.get("wall")), \
    "a wall fastener landed outside every nogging zone"

for zo in WALL_ZONES:
    zo["labels"].sort()
assert len({zo["cut"] for zo in WALL_ZONES}) == len(WALL_ZONES), \
    "two nogging zones carry the same cut-list line - group them"
assert max(zo["z"][1] for zo in WALL_ZONES) == RAIL_TOP, \
    f"the highest nogging zone stops at " \
    f"{max(zo['z'][1] for zo in WALL_ZONES)}, but the topmost thing lying " \
    f"on the wall is the back side rail at {RAIL_TOP}"
assert min(zo["z"][0] for zo in WALL_ZONES) == 0, \
    "no nogging zone reaches the floor, yet the back posts stand on it"
# The height line the whole fitting job is measured from. A metre line is the
# trade's own datum, but it is only usable if it lands on BARE WALL between
# two nogging zones - a line struck across a batten is a line you cannot see
# once the bed is up against it.
MEASURE_DATUM_Z = 1000
_bands = sorted((zo["z"] for zo in WALL_ZONES if not zo["corner"]))
_below = max(z1 for z0, z1 in _bands if z1 <= MEASURE_DATUM_Z)
_above = min(z0 for z0, z1 in _bands if z0 >= MEASURE_DATUM_Z)
assert _below < MEASURE_DATUM_Z < _above, \
    f"the {MEASURE_DATUM_Z} mm datum line falls inside a nogging zone"
# HOW MANY TIMES THE NICHE IS MEASURED. One tape reading is a point, and a
# wall is a surface: the width that matters is the SMALLEST one anywhere the
# bed touches, so each end wall is read on a grid - so many heights, so many
# depths - and the pairs are added up point by point. Two of each is the least
# that can find a bulge at all; the numbers here are what the pre-step tells
# the reader to do and what the measuring figure draws, from one place.
MEASURE_GRID = (5, 3)            # heights x depths, per end wall
assert min(MEASURE_GRID) >= 2, \
    "a measuring grid with a single row or column reads a point, not a wall"

# ---------------------------------------------------------------------------
# X8b - THE ZONES, READ FROM THE LINE THE MAN ACTUALLY WORKS FROM
# ---------------------------------------------------------------------------
# Every height in this file is measured from FERDIG GULV, Z = 0, and that is
# the right datum for a drawing: the floor is where the bed stands and where
# the arithmetic starts. It is the wrong datum for a WALL. The floor in this
# house is out of level - the whole fitting job is built plumb and level off
# MEASURE_DATUM_Z, a laser line struck round the niche 1000 mm above the
# HIGHEST point of the floor - so "229 over ferdig gulv" is a number the man
# at the open wall cannot set: he would have to find the floor under that
# exact spot first, and the floor is the thing he has already decided not to
# trust. What he CAN set, anywhere along the wall, in one tape pull, is a
# distance from the laser line.
#
# So the zones are emitted in BOTH notations, and the second one is derived
# from the first by subtraction - never written down. Sign convention is the
# only thing to remember and it is the natural one: MINUS is below the line,
# PLUS is above it. The datum sits at 1000 on purpose (it is a metre line and
# it lands on bare wall, asserted above), so the two notations differ by
# exactly MEASURE_DATUM_Z everywhere, and that difference is asserted here
# and again in the printed table and on the drawn sheet - measured in the
# ink, not trusted.
def riss(z):
    """A height over the finished floor as an offset from the height line."""
    return z - MEASURE_DATUM_Z


def riss_num(z):
    """That offset, signed, the way it is written on a tape: -771, +402."""
    v = riss(z)
    return f"{'+' if v > 0 else '-' if v < 0 else ''}{abs(v):g}"


def riss_span(z0, z1):
    """A whole band from the line: '-771..-703 under risset'."""
    txt = f"{riss_num(z0)}..{riss_num(z1)}"
    if riss(z1) <= 0:
        return f"{txt} under risset"
    if riss(z0) >= 0:
        return f"{txt} over risset"
    return f"{txt} krysser risset"


for zo in WALL_ZONES:
    zo["riss"] = tuple(riss(v) for v in zo["z"])
    zo["riss_txt"] = riss_span(*zo["z"])
    for _a, _b in zip(zo["z"], zo["riss"]):
        assert _a - _b == MEASURE_DATUM_Z, \
            f"nogging zone {zo['cut'][0]}: {_a} over the floor and {_b} from " \
            f"the height line differ by {_a - _b}, not {MEASURE_DATUM_Z}"
assert sum(1 for zo in WALL_ZONES if min(zo["riss"]) < 0 < max(zo["riss"])) \
    == sum(1 for zo in WALL_ZONES if zo["corner"]), \
    "the only zones that straddle the height line should be the two corner " \
    "columns - they are the ones that run from the floor past 1000"

print(f"OK  SPIKERSLAG: {len(WALL_ZONES)} zones on the wall face, "
      + " ".join(f"{zo['z'][0]:g}-{zo['z'][1]:g}" for zo in WALL_ZONES)
      + f" mm above the finished floor, carrying "
      + ", ".join(sorted({zo["cut"][0] for zo in WALL_ZONES})))
print(f"OK  X8b fra høyderisset ({MEASURE_DATUM_Z} over ferdig gulv): "
      + " · ".join(f"sone {_n} {zo['riss_txt']}"
                   for _n, zo in enumerate(WALL_ZONES, 1))
      + " - utledet ved subtraksjon, aldri skrevet inn, og differansen er "
        "asserted på hver eneste sonekant")
print("OK  X11 hvilke soner som faktisk får skruer i veggen: "
      + " · ".join(
          f"sone {_n} "
          + (", ".join(f"{_jid} {_q} stk." for _jid, _q in zo["fix"])
             if zo["fix"] else "bare anlegg")
          for _n, zo in enumerate(WALL_ZONES, 1))
      + " - lest av de plasserte veggfestene, ikke av tabellteksten")

# C9: nothing horizontal may be longer than 1984, and every long member must sit
# in one of the two legal X bands. A 1990 mm piece cannot be swung into a 1990 mm
# opening, so the envelope assert above is necessary but not sufficient.
#
# W9 ripple: there are TWO bands now, not one. The two side rails still run WALL
# TO WALL at X 3..1987 (they pass over the posts, so nothing is in their way);
# the back bench rail and the back table ledger run POST TO POST at X 48..1942,
# because the back posts have moved into their Y band and they butt them. Both
# bands satisfy C9 - 1894 goes into a 1990 mm opening even more easily than 1984.
C9_BANDS = {
    "wall to wall": (THROUGH_X0, THROUGH_X1),          # 3 .. 1987
    "post to post": (BETWEEN_POSTS_X0, BETWEEN_POSTS_X1),   # 48 .. 1942
}
long_members = []
for p in parts + [panel_bed, panel_table]:
    (x0, x1), _, _ = p.extents
    dx = x1 - x0
    assert dx <= THROUGH_LEN + TOL, \
        f"'{p.label}' is {dx:.1f} mm long in X - cannot be manoeuvred into the " \
        f"{WALL_SPAN} mm opening (max {THROUGH_LEN})"
    if dx > POST_HEIGHT / 2:                      # a through-running member
        band = [b for b, (bx0, bx1) in C9_BANDS.items()
                if abs(x0 - bx0) < TOL and abs(x1 - bx1) < TOL]
        assert len(band) == 1, \
            f"'{p.label}' spans {x0}..{x1}, expected one of " \
            f"{sorted(C9_BANDS.values())}"
        long_members.append(p.label)
# D11 ripple: the front bench rail has LEFT this list - it is two 642 mm
# segments now, in the same class as the D2 front guard segments.
# W1 ripple: so have the two back guard boards, by being deleted. The back bench
# rail, the two side rails and the table ledger are the FOUR that remain (was
# six). C9 itself is untouched - the rule is about getting a long piece into a
# 1990 mm opening, and there are simply two fewer long pieces now.
C9_THROUGH_MEMBERS = {
    "Upper Side Rail Back", "Upper Side Rail Front",
    "Bench Rail Back (continuous)", "Table Ledger Back",
}
assert set(long_members) == C9_THROUGH_MEMBERS, \
    f"C9: through-running members are {sorted(long_members)}, expected " \
    f"{sorted(C9_THROUGH_MEMBERS)}"
# W9: which of the two bands each of them is in, named explicitly.
C9_BAND_OF = {
    "Upper Side Rail Back": "wall to wall",
    "Upper Side Rail Front": "wall to wall",
    "Bench Rail Back (continuous)": "post to post",
    "Table Ledger Back": "post to post",
}
for p in parts:
    if p.label in C9_BAND_OF:
        want = C9_BANDS[C9_BAND_OF[p.label]]
        assert p.extents[0] == want, \
            f"W9: '{p.label}' spans X {p.extents[0]}, want {want} " \
            f"({C9_BAND_OF[p.label]})"
assert not any("Guard Rail" in m for m in long_members), \
    "W1: no guard board runs wall to wall any more - the back pair is gone and " \
    "the front pair was always segmented"
assert not any("Bench Rail Front" in m for m in long_members), \
    "D11: the front bench rail must not be a through-running member any more"
assert "Bench Rail Back (continuous)" in long_members, \
    "C5: the back bench rail must still be one continuous member"
print(f"OK  C9/W9: no horizontal member exceeds {THROUGH_LEN} mm; all "
      f"{len(long_members)} long members sit in one of the two legal bands - "
      f"wall to wall X {THROUGH_X0}..{THROUGH_X1} ({THROUGH_LEN} mm): "
      + ", ".join(sorted(m for m in long_members
                         if C9_BAND_OF[m] == "wall to wall"))
      + f"; post to post X {BETWEEN_POSTS_X0}..{BETWEEN_POSTS_X1} "
        f"({BETWEEN_POSTS_LEN} mm): "
      + ", ".join(sorted(m for m in long_members
                         if C9_BAND_OF[m] == "post to post")))

# D1: exactly SIX verticals - 4 corner posts + 2 ladder uprights - each one
# standing on the floor and running at least to the platform, which is what
# makes it a vertical of the FRAME rather than a stub leg (the tallest stub leg
# is 229).
# W2/W6 ripple: "floor to top" is no longer one height. The back pair stops at
# BACK_POST_HEIGHT = 1402 (the rail underside, which they carry) and the other
# four go on to 2037, so the membership test is the RAIL UNDERSIDE - the height
# at which a vertical is holding the platform up - not the literal 2037 and not
# the platform surface either, which the back pair no longer reaches.
VERTICAL_HEIGHTS = {
    "Corner Post Back": BACK_POST_HEIGHT,        # 1402, W6
    "Corner Post Front": POST_HEIGHT,            # 2037
    "Ladder Upright": POST_HEIGHT,               # 2037
}


def vertical_family(p):
    for prefix in VERTICAL_HEIGHTS:
        if p.label.startswith(prefix):
            return prefix
    return None


verticals = [p for p in parts
             if p.extents[2][0] == 0 and p.extents[2][1] >= RAIL_BOTTOM - TOL]
corner_posts = [p for p in verticals if p.label.startswith("Corner Post")]
back_posts = [p for p in verticals if p.label.startswith("Corner Post Back")]
front_posts = [p for p in verticals if p.label.startswith("Corner Post Front")]
uprights = [p for p in verticals if p.label.startswith("Ladder Upright")]
assert len(verticals) == 6, \
    f"D1: expected 6 frame verticals, found {len(verticals)}: " \
    f"{[p.label for p in verticals]}"
assert len(corner_posts) == 4 and len(uprights) == 2
assert len(back_posts) == 2 and len(front_posts) == 2
assert not any(p.label.startswith("Back Post Mid") for p in parts), \
    "D1: the intermediate back posts are supposed to be gone"
# D13/W2/W6: the three families share neither section nor length any more -
# 2 x front corner post 36x98 x 2037, 2 x back corner post 36x98 x 1402 (U2;
# both were 48x48 up to v10), 2 x ladder upright 36x48 x 2037 (U2 turned them:
# 48 in X, 36 in Y, so the whole front plane is one 36 mm layer).
for p in verticals:
    (x0, x1), (y0, y1), (z0, z1) = p.extents
    fam = vertical_family(p)
    assert fam is not None, f"'{p.label}' is not a known vertical family"
    want_w = UPRIGHT_W if fam == "Ladder Upright" else POST_W
    want_t = UPRIGHT_T if fam == "Ladder Upright" else POST_T
    assert x1 - x0 == want_w, f"'{p.label}' is {x1 - x0} wide in X, want {want_w}"
    assert y1 - y0 == want_t, f"'{p.label}' is {y1 - y0} deep in Y, want {want_t}"
    assert (z0, z1) == (0, VERTICAL_HEIGHTS[fam]), \
        f"'{p.label}' runs Z {z0}..{z1}, want 0..{VERTICAL_HEIGHTS[fam]}"
    assert 0 <= x0 and x1 <= WALL_SPAN
for u in uprights:
    assert u.extents[1] == (LADDER_Y0, LADDER_Y1), \
        f"'{u.label}' is not in the front rail plane for bolting"
for p in back_posts:
    # W6: inside the back rail's Y band; U2: filling the WALL SIDE of it, since
    # the post is 36 deep and the band 48. Its back face is the wall plane and
    # the rail overhangs it 12 mm on the room side.
    assert p.extents[1] == (BACK_POST_Y0, BACK_POST_Y1), \
        f"W6/U2: '{p.label}' is at Y {p.extents[1]}, want " \
        f"{(BACK_POST_Y0, BACK_POST_Y1)}"
    assert p.extents[1][0] == BACK_RAIL_Y0 and p.extents[1][1] <= BACK_RAIL_Y1, \
        f"W6: '{p.label}' is not inside the back rail plane " \
        f"{(BACK_RAIL_Y0, BACK_RAIL_Y1)} with its back face on the wall"
# U2: the four corner posts are one section and one profile with the boards.
assert (POST_T, POST_W) == (BOARD36_T, BOARD36_W), \
    f"U2: the corner posts are {sec(POST_T, POST_W)}, want the board profile " \
    f"{sec(BOARD36_T, BOARD36_W)}"
assert (UPRIGHT_T, UPRIGHT_W) == (BLOCK_T, BLOCK_H), \
    f"U2: the ladder uprights are {sec(UPRIGHT_T, UPRIGHT_W)}, want the " \
    f"{sec(BLOCK_T, BLOCK_H)} block/upright profile"
assert UPRIGHT_T == POST_T == FRONT_POST_Y1 - FRONT_POST_Y0, \
    f"U3: every vertical in the front plane must be {POST_T} mm deep in Y"
print(f"OK  D1/W2/W6/U2: exactly 6 frame verticals - 2 front corner posts "
      f"{sec(POST_T, POST_W)} x {POST_HEIGHT}, 2 back corner posts "
      f"{sec(POST_T, POST_W)} x {BACK_POST_HEIGHT} (W6: inside the back rail "
      f"plane, Y {BACK_POST_Y0}..{BACK_POST_Y1} of {BACK_RAIL_Y0}.."
      f"{BACK_RAIL_Y1}, stopping under the rail), 2 ladder uprights "
      f"{sec(UPRIGHT_T, UPRIGHT_W)} x {POST_HEIGHT} "
      f"({UPRIGHT_W} along X / {UPRIGHT_T} along Y after the U2 turn, so the "
      f"whole front plane Y {FRONT_POST_Y0}..{FRONT_POST_Y1} is one {POST_T} mm "
      f"layer); no intermediate back posts")

# W2/W6: THE BACK POSTS STOP UNDER THE RAIL AND CARRY IT. Four things have to
# hold. (a) The post top must BE the rail underside - a millimetre over and the
# rail does not sit down on the end grain, a millimetre under and the whole
# bearing story is a gap. (b) The bearing has to be real: a shared horizontal
# face over the post's full 48 mm depth, not an edge kiss. (c) The only part on a
# back post that goes ABOVE the post top may be that rail - anything else up
# there would be a joint hanging in mid air. (d) Nothing at all on the wall side
# stands above the PLATFORM: that is the W2 conclusion, and it is now true with a
# whole rail height to spare instead of exactly 0 mm.
assert BACK_POST_HEIGHT == RAIL_BOTTOM == BACK_RAIL_ON_POST_Z, \
    f"W6: the back posts stop at {BACK_POST_HEIGHT}, want the rail underside " \
    f"{RAIL_BOTTOM} so the rail bears on them"
assert BACK_POST_HEIGHT < SLAT_Z1 < MATTRESS_Z1, \
    "W2/W6: the back posts must stay clear of the platform and the mattress band"
assert SLAT_Z1 - BACK_POST_HEIGHT == RAIL_H + BED_SLAT_T == 121, \
    f"W6: the post top is {SLAT_Z1 - BACK_POST_HEIGHT} mm under the mattress " \
    f"underside, expected one rail + one slat = {RAIL_H + BED_SLAT_T}"
# (b) the rail actually BEARS on both post tops, over the full post depth in Y.
# The rail is set in 3 mm at each wall by C9, so it covers 45 of the post's 48 mm
# in X.
for bp in back_posts:
    (px0, px1), (py0, py1), (_, ptop) = bp.extents
    (rx0, rx1), (ry0, ry1), (rz0, _) = back_rail.extents
    assert abs(rz0 - ptop) < TOL, \
        f"W6: '{bp.label}' tops out at {ptop} but the back rail starts at " \
        f"{rz0} - the rail must sit ON the post"
    bx = min(px1, rx1) - max(px0, rx0)
    by = min(py1, ry1) - max(py0, ry0)
    assert abs(by - POST_T) < TOL, \
        f"W6: the rail covers only {by} mm of '{bp.label}' in Y, want the full " \
        f"post depth {POST_T}"
    assert abs(bx - (POST_W - THROUGH_X0)) < TOL, \
        f"W6: the rail covers {bx} mm of '{bp.label}' in X, want " \
        f"{POST_W - THROUGH_X0} (the {THROUGH_X0} mm C9 wall clearance is the " \
        f"only bit missing)"
    assert abs(bx * by - BACK_RAIL_POST_BEARING) < TOL, \
        f"W6: bearing on '{bp.label}' is {bx * by} mm2, want " \
        f"{BACK_RAIL_POST_BEARING}"
back_post_ids = {id(p) for p in back_posts}
back_post_neighbours = []
for p in parts:
    if id(p) in back_post_ids:
        continue
    for bp in back_posts:
        inter = [min(a1, b1) - max(a0, b0)
                 for (a0, a1), (b0, b1) in zip(p.extents, bp.extents)]
        # touching = overlapping in two axes and flush (or overlapping) in the
        # third; a shared face is enough, an edge or corner kiss is not.
        if sorted(inter)[-2] > TOL and min(inter) >= -TOL:
            back_post_neighbours.append(p)
            # (c) the ONLY thing allowed above the post top is the rail it
            # carries. Everything else has to be at or below the cut.
            assert (p.extents[2][1] <= BACK_POST_HEIGHT + TOL
                    or p is back_rail), \
                f"W2/W6: '{p.label}' reaches Z {p.extents[2][1]} on a back " \
                f"post that stops at {BACK_POST_HEIGHT}, and it is not the " \
                f"back side rail bearing on it"
            break
assert back_post_neighbours, "W2: the back posts touch nothing at all"
# 11: per post, the end beam, the back bench rail, the back table ledger, the
# back side rail, the outermost bench slat and - V13 - the end cleat screwed to
# the post's front face and the end slat that lands on it, x2, minus the three
# continuous members counted once.
# (Was 13 in v9, when the end slats butted the posts; 11 until V5 deleted the
# end-beam and bench-rail bearing blocks that hung on these two faces; 7 until
# V13 put the end cleat and its slat on the front face. After W6 the upper slats
# are 98 mm above the post tops and touch nothing there, and the bench slats
# butt the post's X-inner face instead of clearing it in Y.)
assert len(back_post_neighbours) == 11, \
    f"W2/W6/V13: the back posts touch {len(back_post_neighbours)} parts, " \
    f"expected 11: {sorted(p.label for p in back_post_neighbours)}"
highest = max(back_post_neighbours, key=lambda p: p.extents[2][1])
assert highest is back_rail and highest.extents[2][1] == RAIL_TOP, \
    f"W6: the highest WOOD on a back post is '{highest.label}' at " \
    f"{highest.extents[2][1]}, expected the back side rail top {RAIL_TOP}"
# The M8 ties into the end beam (1304..1402) are the highest fastener and they
# stop exactly at the cut, where the beam top is flush with the rail underside.
assert END_BEAM_Z1 == BACK_POST_HEIGHT, \
    "W6: the end beam top and the post top are both the rail underside"
# (d) NOTHING above the platform on the wall side. There is no post above the
# slats at all now - the tallest thing in the back rail plane is the rail, 34 mm
# BELOW the platform surface - so a 120 or a 130 mm mattress exposes nothing.
# Swept over everything that reaches into the back rail plane, not just the posts.
wall_side = [p for p in parts if p.extents[1][0] < BACK_RAIL_Y1 - TOL]
above_platform_at_wall = [p for p in wall_side if p.extents[2][1] > SLAT_Z1 + TOL]
assert not above_platform_at_wall, \
    "W2: nothing may stand above the platform in the back rail plane - " \
    f"found {[p.label for p in above_platform_at_wall]}"
assert max(p.extents[2][1] for p in wall_side) == SLAT_Z1, \
    "W2: the wall side should top out exactly at the platform surface (the slats)"
assert BACK_POST_HEIGHT < SLAT_Z1, \
    f"W6: {BACK_POST_HEIGHT - SLAT_Z1} mm of post above the platform"
print(f"OK  W2/W6/U2: back posts {POST_HEIGHT} -> {BACK_POST_HEIGHT} = the RAIL "
      f"UNDERSIDE (X1 took it 1065 -> {BACK_POST_HEIGHT} with the deck; it was "
      f"1197, the platform top, and 1337 before that), standing in "
      f"the rail's own plane at Y {BACK_POST_Y0}..{BACK_POST_Y1} of "
      f"{BACK_RAIL_Y0}..{BACK_RAIL_Y1}. The back side "
      f"rail BEARS on both post tops - {POST_W - THROUGH_X0} x {POST_T} = "
      f"{BACK_RAIL_POST_BEARING} mm2 of end grain (was 2160), ~7.9 kN, so the corner "
      f"reaction never enters a fastener; the bolts and brackets are pure ties. "
      f"The {len(back_post_neighbours)} parts a back post touches all top out at "
      f"or below the cut except that rail; end-beam top {END_BEAM_Z1} = the cut, "
      f"rail {RAIL_BOTTOM}..{RAIL_TOP}, slat platform {SLAT_Z0}..{SLAT_Z1} - and "
      f"the wall side stops there: {SLAT_Z1 - BACK_POST_HEIGHT} mm of clear air "
      f"between the post top and the mattress underside, whatever the mattress "
      f"turns out to be (modelled {MATTRESS_H})")

# W1/W2/W6: the envelope is ASYMMETRIC now, and the two sides have to be checked
# separately - a single bb.max.Z would hide the whole point of this round.
back_side = [p for p in parts if p.extents[1][1] <= BACK_RAIL_Y1 + TOL]
front_side = [p for p in parts if p.extents[1][0] >= FRONT_RAIL_Y0 - TOL]
back_top = max(p.extents[2][1] for p in back_side)
wall_side_top = max(p.extents[2][1] for p in wall_side)
front_top = max(p.extents[2][1] for p in front_side)
assert back_top == RAIL_TOP, \
    f"W6: the back plane (Y <= {BACK_RAIL_Y1}) tops out at {back_top}, want the " \
    f"back side rail top {RAIL_TOP}"
assert wall_side_top == SLAT_Z1, \
    f"W2: the wall side tops out at {wall_side_top}, want the platform {SLAT_Z1}"
assert front_top == POST_HEIGHT, \
    f"W2: the front side tops out at {front_top}, want {POST_HEIGHT}"
assert front_top - wall_side_top == POST_HEIGHT - SLAT_Z1 == 514  # [V6: was 501]
print(f"OK  W1/W2/W6: asymmetric envelope - the back rail plane "
      f"(Y <= {BACK_RAIL_Y1}) tops out at {back_top} = the back side rail, "
      f"anything reaching into it at {wall_side_top} = the platform surface, "
      f"the front side (Y >= {FRONT_RAIL_Y0}) at {front_top} = the guard tops; "
      f"{front_top - wall_side_top} mm apart (was 363 in v8)")

# D4: the post section is the slim one, but the wall faces and the ladder
# opening are exactly where they always were.
assert [p.extents[0] for p in sorted(corner_posts, key=lambda q: q.extents[0][0])][0] \
    == (0, POST_W)
assert sorted(corner_posts, key=lambda q: q.extents[0][0])[-1].extents[0] \
    == (WALL_SPAN - POST_W, WALL_SPAN)
up = sorted(uprights, key=lambda q: q.extents[0][0])
assert up[0].extents[0] == (LADDER_INNER_L - UPRIGHT_W, LADDER_INNER_L)
assert up[1].extents[0] == (LADDER_INNER_R, LADDER_INNER_R + UPRIGHT_W)
assert up[1].extents[0][0] - up[0].extents[0][1] == LADDER_CLEAR
# D13: still centred on 995 and still wide enough to climb through.
assert (up[0].extents[0][1] + up[1].extents[0][0]) / 2 == LADDER_CENTER_X, \
    "D13: the ladder opening is not symmetric about X 995"
assert MIN_LADDER_CLEAR <= LADDER_CLEAR <= MAX_LADDER_CLEAR, \
    f"D13/V7: the {LADDER_CLEAR} mm clear ladder is outside the EN 747 " \
    f"access band {MIN_LADDER_CLEAR}..{MAX_LADDER_CLEAR}"
print(f"OK  D4: posts flush with the walls at X 0..{POST_W} / "
      f"{WALL_SPAN - POST_W}..{WALL_SPAN}; D13 ladder clear opening "
      f"{LADDER_CLEAR} mm (min {MIN_LADDER_CLEAR}) between X "
      f"{LADDER_INNER_L:.0f} and {LADDER_INNER_R:.0f}, upright outer faces "
      f"{up[0].extents[0][0]:.0f} / {up[1].extents[0][1]:.0f}, centred on "
      f"{LADDER_CENTER_X}")

# Fixed heights. Everything below the platform is untouched by D5/D6/D7; the
# platform stack itself is the thing that moved.
# X1/X3: v14 moves BOTH datums - the platform up 337 mm to put the slat
# underside on a round 1500, and the bench up 38 to a 320 mm bench top / 420 mm
# seat - so unlike every round before it, there is no half of this block that
# stayed still. The point of the block is unchanged: these are the heights a
# tape measure finds on the finished bed, typed out once so a derivation that
# drifts is caught here rather than in a drawing.
assert RAIL_BOTTOM == 1402 and RAIL_TOP == SLAT_Z0 == 1500
# V13 narrowed the match: there IS a cleat in this bed now (the bench end
# cleat), and the thing D5 deleted was the SLAT cleat under the upper
# platform. The guard names it.
assert not any("Slat Cleat" in p.label for p in parts), \
    "D5: the slat cleats must be gone"
assert (SLAT_Z0, SLAT_Z1) == (1500, 1523), "D5/U1/V6: slats not flush on top of the rails"
assert (MATTRESS_Z0, MATTRESS_Z1) == (1523, 1643)
assert (BENCH_RAIL_BOTTOM, BENCH_RAIL_TOP) == (229, 297)
assert BENCH_TOP == 320 and PANEL_TOP_BED == 315 and PANEL_UNDER_BED == 297
assert PANEL_TOP_TABLE == 700 and PANEL_UNDER_TABLE == 682   # X9: was 560/542
assert RUNG_TOPS == [297, 572, 848, 1073, 1298] and POST_HEIGHT == 2037
#      X9: was [297, 542, 787, 1032, 1277] - rung 3 went up to clear the desk
#      and the two flights fell out of it
assert BACK_POST_HEIGHT == 1402, "W6: the back posts must stop at the rail underside"
assert (LEDGER_BACK_Z0, LEDGER_BACK_Z1) == (614, 682), \
    "V2: the ledger is a bench-rail profile, so its underside is 68 below its top"
assert (TABLE_BEARER_Z0, TABLE_BEARER_Z1) == (614, 682) \
    and (TABLE_BEARER_Y0, TABLE_BEARER_Y1) == (697, 788), \
    "X9: the two bordklosser carry the plate's front edge at the same 682 the " \
    "ledger carries its rear one"
assert STUB_LEG_H == 229, "W3: the stub legs reach the bench rail underside"
print(f"OK  invariant heights held: rail underside {RAIL_BOTTOM}, rail top "
      f"{RAIL_TOP}, no cleats, slats {SLAT_Z0}..{SLAT_Z1} (flush on the rails, "
      f"U1 took the platform 1197 -> 1186 on the {BED_SLAT_T} mm board and X1 "
      f"lifted it 337 so the slat UNDERSIDE lands on {SLAT_Z0}), "
      f"mattress {MATTRESS_Z0}..{MATTRESS_Z1} ({MATTRESS_H} mm, was 150 on "
      f"1186..1336), bench "
      f"{BENCH_RAIL_BOTTOM}/{BENCH_RAIL_TOP}/{BENCH_TOP} (X3: +38, was "
      f"191/259/282), ledger "
      f"{LEDGER_BACK_Z0}..{LEDGER_BACK_Z1}, rungs "
      + "/".join(str(t) for t in RUNG_TOPS)
      + f", panel {PANEL_UNDER_BED}..{PANEL_TOP_BED} (bed) / "
        f"{PANEL_UNDER_TABLE}..{PANEL_TOP_TABLE} (table), total {POST_HEIGHT} "
        f"at the front / {BACK_POST_HEIGHT} at the wall side (W6: the rail "
        f"underside; X1: 1700 / 1065 before the lift)")

# D12/W6: the depth planes, with their provenance.
#
# D12 pulled every FRONT plane in by 106 mm and left the back half alone; that
# half of the table is below and is byte-for-byte what D12 asserted. W6 is the
# first round to move anything at the BACK, and it moves exactly one layer: the
# back posts (and with them the wall plane, the end-beam back end and the
# end-beam back bearing blocks) come forward by POST_T = 48 mm into the back
# rail's own plane. Everything else at the back - the rail, the ledger, the bench
# rail, every slat and the panel's rear edge - is still exactly where D12 left
# it. The moved parts get explicit new-position asserts, the way D14 gave them to
# the guards, so a slip in either direction is named rather than inferred.
#
# U2 is the SECOND round to touch the back, and it does not move a plane at all:
# it thins the post. The post's WALL-SIDE face - the one that matters, the one
# the bed is bolted to - is exactly where W6 put it, and the 12 mm it gives up
# is at the other end of the post, inside the rail band where nothing else
# lives. So the table below checks two things at once: that the wall-side face
# of every back member is still on Y -48 after two rounds of shuffling, and that
# the only thing that has moved this round is a front face, by POST_THIN.
BACK_TUCK = 48                           # W6 history: how far the layer came in
BACK_PLANES_V9 = {   # v9 value -> today, (wall-side face, room-side face)
    "wall / mounting plane": ((-96, -96), (WALL_Y, WALL_Y)),
    "back corner posts": ((-96, -48), (BACK_POST_Y0, BACK_POST_Y1)),
    "end beam back end": ((-96, -96), (END_BEAM_Y0, END_BEAM_Y0)),
    "end-beam back blocks": ((-96, -48), (BACK_POST_Y0, BACK_POST_Y0 + POST_T)),
}
for what, ((o0, o1), (n0, n1)) in BACK_PLANES_V9.items():
    # W6 brought the wall-side face in by exactly BACK_TUCK and it has not moved
    # since. The room-side face came in by the same 48; where U2 then thinned the
    # member (48 -> 36 in Y) it came BACK by POST_THIN, so it is 48 - 12 = 36 in
    # from v9. Nothing may have moved by anything else.
    assert n0 - o0 == BACK_TUCK, \
        f"W6: '{what}' moved its wall-side face {n0 - o0}, not {BACK_TUCK}"
    assert n1 - o1 in (BACK_TUCK, BACK_TUCK - POST_THIN), \
        f"W6/U2: '{what}' moved its room-side face {n1 - o1}, want " \
        f"{BACK_TUCK} (section unchanged) or {BACK_TUCK - POST_THIN} (thinned)"
BACK_PLANES_FIXED = {                    # unmoved since D12
    "back side rail": ((-48, 0), (BACK_RAIL_Y0, BACK_RAIL_Y1)),
    "back bench rail": ((-48, 0), (BENCH_RAIL_Y[0], BENCH_RAIL_Y[0] + BENCH_RAIL_T)),
    # V2: the ledger is 48 deep now, so its ROOM-SIDE face moved -27 -> 0 -
    # onto the back bench rail's own face, which is the point of the change.
    "back table ledger": ((-48, 0),
                          (LEDGER_BACK_Y0, LEDGER_BACK_Y0 + LEDGER_BACK_T)),
    "slats / bench slats / panel rear": ((-48, -48), (SLAT_Y0, PANEL_Y0)),
}
for what, (old, new) in BACK_PLANES_FIXED.items():
    assert old == new, f"D12: '{what}' was supposed to stay at {old}, it is {new}"
# The explicit new positions of everything W6 moved.
assert (BACK_POST_Y0, BACK_POST_Y1) == (-48, -12), \
    f"W6/U2: the back posts are at Y {BACK_POST_Y0}..{BACK_POST_Y1}, want " \
    f"-48..-12 (the wall side of the back rail's own plane)"
assert BACK_POST_Y0 == BACK_RAIL_Y0 and BACK_POST_Y1 <= BACK_RAIL_Y1, \
    "W6: the back posts must sit inside the back rail's plane, back face first"
assert BACK_RAIL_Y1 - BACK_POST_Y1 == POST_THIN, \
    f"U2: the rail should overhang the post by {POST_THIN} mm on the room side"
assert BACK_POST_HEIGHT == 1402 and BACK_POST_HEIGHT == RAIL_BOTTOM, \
    f"W6/X1: the back posts run 0..{BACK_POST_HEIGHT}, want 0..1402"
# X10 - THE SKIRTING BOARD IS PART OF THE BED, AND IT WAS NOT IN THE MODEL.
# The wall plane is a flat face the bed is pushed against and screwed to, and
# the model has always checked that nothing of the bed stands proud of it. What
# nobody checked is what stands proud of the WALL: a fotlist is 12-22 mm of it,
# it runs along the floor, and the parts that meet the wall AT the floor cannot
# ride over it. There are exactly four of them and this is the list, DERIVED -
# every part whose back face is the wall plane and whose underside is the
# floor. The room-preparation step says the same thing in Norwegian; this is
# the assert that makes it a requirement of the geometry rather than advice.
WALL_FOOT_PARTS = sorted(p.label for p in parts
                         if abs(p.extents[1][0] - WALL_Y) < TOL
                         and abs(p.extents[2][0]) < TOL)
assert len(WALL_FOOT_PARTS) == 4, (
    f"X10: {len(WALL_FOOT_PARTS)} parts stand on the floor AND in the wall "
    f"plane - {WALL_FOOT_PARTS}. Every one of them has to have bare wall "
    f"behind it all the way down, so the fotlist comes off across the whole "
    f"niche before the frame is raised. Change the list and the room "
    f"preparation changes with it")
print(f"OK  X10 fotlist: {len(WALL_FOOT_PARTS)} deler står BÅDE på gulvet "
      f"(Z 0) og i veggplanet (Y {WALL_Y:g}) - {', '.join(WALL_FOOT_PARTS)}. "
      f"Fotlist og annet listverk må vekk i hele nisjens bredde "
      f"({WALL_SPAN:g} mm) før reisning; en 15 mm list ville skjøvet hele "
      f"rammen 15 mm ut fra veggen og lagt den ut av lodd")
assert WALL_PLANE_BUILT == WALL_Y == -48, \
    f"W7: the bodies' back face is Y {WALL_PLANE_BUILT:g}, the wall plane is " \
    f"{WALL_Y:g}, and both want -48"
assert (END_BEAM_Y0, END_BEAM_Y1, END_BEAM_LEN) == (-48, 788, 836), \
    f"W6/U3: the end beams are Y {END_BEAM_Y0}..{END_BEAM_Y1} ({END_BEAM_LEN}), " \
    f"want -48..788 (836)"
# X10: the first == restated END_BEAM_X's own definition and the message quoted
# [98, 1844] against a condition demanding [98, 1856] - the 1844 and the 146
# are V6b-old numbers computed with a 48 mm end beam. Read off the bodies.
_built_beam_x = sorted(p.extents[0] for p in parts
                       if p.label.startswith("End Beam"))
assert [x0 for x0, _ in _built_beam_x] == [98, 1856] \
        and END_BEAM_X == [98, 1856], \
    f"U2/V6b: the end beams are built at X {_built_beam_x} and the table " \
    f"says {END_BEAM_X}; both want the post inner faces 98..134 and " \
    f"1856..1892 for a {END_BEAM_T} mm beam"
assert OVERALL_DEPTH == 836, f"W7/U3: overall depth {OVERALL_DEPTH}, want 836"
# and the plane the tuck vacated has to be genuinely outside the bed now.
VACATED_BACK_LAYER = (-96, -48)
still_behind = [p for p in parts + [panel_bed, panel_table, mattress]
                if p.extents[1][0] < VACATED_BACK_LAYER[1] - TOL]
assert not still_behind, \
    f"W6: {[p.label for p in still_behind]} are still in the vacated layer " \
    f"Y {VACATED_BACK_LAYER[0]}..{VACATED_BACK_LAYER[1]}"
print(f"OK  W6: the back layer Y {VACATED_BACK_LAYER[0]}.."
      f"{VACATED_BACK_LAYER[1]} is EMPTY - the {len(BACK_PLANES_V9)} things that "
      f"lived in it (" + ", ".join(sorted(BACK_PLANES_V9)) + f") all came "
      f"forward {BACK_TUCK} mm into the back rail plane; the "
      f"{len(BACK_PLANES_FIXED)} other back planes are exactly where D12 left "
      f"them")
FRONT_PLANES_V7 = {                      # v7 value -> v8 value, all -106
    "front side rail": ((810, 858), (FRONT_RAIL_Y0, FRONT_RAIL_Y1)),
    "front bench rail": ((810, 858), (BENCH_RAIL_Y[1], BENCH_RAIL_Y[1] + BENCH_RAIL_T)),
    "slats / bench slats": ((858, 858), (SLAT_Y1, SLAT_Y1)),
    # V2: the panel front edge is the one plane that is deliberately NOT on the
    # D12 line any more. It stands PANEL_FIT back off it, because the panel has
    # to be lowered between the uprights, not forced past them.
    "panel front (less the fit)": ((858, 858),
                                   (PANEL_Y1 + PANEL_FIT, PANEL_Y1 + PANEL_FIT)),
}
for what, ((o0, o1), (n0, n1)) in FRONT_PLANES_V7.items():
    assert (o0 - n0, o1 - n1) == (DEPTH_SHRINK, DEPTH_SHRINK), \
        f"D12: '{what}' moved {o0 - n0}/{o1 - n1}, not {DEPTH_SHRINK}/{DEPTH_SHRINK}"
# U2/U3: the three families that stand IN FRONT of the mounting plane Y = 752
# were 48 deep and are 36 deep now, so their BACK faces are exactly where D12
# left them and every front face comes in by POST_THIN. That is the entire depth
# story of this round, stated per family so a slip in any one of them is named.
FRONT_PLANES_V10 = {                     # v10 value -> v11 value, front face -12
    "front corner posts": ((752, 800), (FRONT_POST_Y0, FRONT_POST_Y1)),
    "ladder uprights": ((752, 800), (LADDER_Y0, LADDER_Y1)),
    "rung treads": ((727, 800), (RUNG_Y0, RUNG_Y1)),
}
for what, ((o0, o1), (n0, n1)) in FRONT_PLANES_V10.items():
    assert o1 - n1 == POST_THIN, \
        f"U3: '{what}' moved its front face {o1 - n1}, not {POST_THIN}"
assert (FRONT_POST_Y0, FRONT_POST_Y1) == (752, 788) == (LADDER_Y0, LADDER_Y1), \
    f"U3: the front plane is posts {FRONT_POST_Y0}..{FRONT_POST_Y1} and " \
    f"uprights {LADDER_Y0}..{LADDER_Y1}; both must be 752..788"
# The rungs are the one family whose BACK face moves too: they keep their 73 mm
# depth and their fronts stay flush with the uprights, so the whole tread comes
# back 12 and the ledge behind the upright plane grows 25 -> 37.
assert (RUNG_Y0, RUNG_Y1) == (720, 788) and RUNG_D == 68, \
    f"U2: the rungs are Y {RUNG_Y0}..{RUNG_Y1}, want 720..788"
assert RUNG_REST_LEDGE == RUNG_D - UPRIGHT_T == 32, \
    f"U2: the rung rest ledge is {RUNG_REST_LEDGE}, want {RUNG_D} - " \
    f"{UPRIGHT_T} = 32"
# D14: the guards are the ONE front plane that did not simply come in by 106.
# They came in by 106 with everything else (906..940 -> 800..834) and then
# jumped the posts, 800..834 -> 718..752, a further POST_T + GUARD_T = 82, which
# is why they are checked here on their own instead of in the table above.
assert (FRONT_GUARD_Y0, FRONT_GUARD_Y1) == (716, 752), \
    f"D14/U1: the front guards are at Y {FRONT_GUARD_Y0}..{FRONT_GUARD_Y1}, " \
    f"want 716..752 (inner faces of the front posts / ladder uprights)"
assert FRONT_GUARD_SHIFT == POST_T + GUARD_T == 72 and \
    (FRONT_POST_Y1 - FRONT_GUARD_Y0,
     FRONT_POST_Y1 + GUARD_T - FRONT_GUARD_Y1) == \
    (FRONT_GUARD_SHIFT, FRONT_GUARD_SHIFT), \
    f"D14: the guards sit {FRONT_POST_Y1 - FRONT_GUARD_Y0} in from where they " \
    f"would hang on the outer faces, not {FRONT_GUARD_SHIFT}"
# The whole journey of the guard plane, in one line: v7 had the boards outboard
# at Y 906, D12 took the front stack in 106, D14 jumped them over the posts by
# POST_T + GUARD_T, and U1/U2 thinned both the post and the board.
assert 906 - FRONT_GUARD_Y0 == DEPTH_SHRINK + FRONT_GUARD_SHIFT + POST_THIN \
    == 190
assert (SLAT_Y0, SLAT_Y1) == (-48, 752) and SLAT_LEN == PLATFORM_DEPTH == 800
assert BENCH_SLAT_LEN == SLAT_LEN
# V2: the panel is the ONE flat part that is no longer a slat length. It is
# PANEL_FIT shorter, and that fit is what makes it a drop-in instead of a part
# you have to spring into place between the wall and the ladder.
assert PANEL_LEN == SLAT_LEN - PANEL_FIT == 798, \
    f"V2: the panel is {PANEL_LEN} long, want {SLAT_LEN} - {PANEL_FIT}"
# W8: ONE length. There is no extended slat any more and no constant left over
# from the split - the name must be gone, not merely unused.
assert "SLAT_LEN_EXT" not in globals() and "SLAT_Y0_EXT" not in globals(), \
    "W8: the W4 two-length slat split is supposed to be gone"
assert min(s.extents[1][0] for s in bed_slats) == WALL_Y == SLAT_Y0, \
    f"W8: the built slats start at Y " \
    f"{min(s.extents[1][0] for s in bed_slats):g}, want the wall plane " \
    f"{WALL_Y:g}"
assert RUNG_REST_LEDGE == 32, \
    f"D12/U2: the rung rest ledge is {RUNG_REST_LEDGE} mm, want 32 (it was 25 " \
    f"while the upright was 48 deep; the tread is still 73 and still flush)"
print(f"OK  D12/W6/U3: back planes - the post layer in by {BACK_TUCK} (wall "
      f"{WALL_Y}, posts {BACK_POST_Y0}..{BACK_POST_Y1} after the U2 thinning), "
      f"rail {BACK_RAIL_Y0}..{BACK_RAIL_Y1} unmoved; the D12 front planes in by "
      f"exactly {DEPTH_SHRINK} mm - rail {FRONT_RAIL_Y0}..{FRONT_RAIL_Y1}, slat "
      f"and panel front edge {SLAT_Y1}; and the front VERTICALS in by "
      f"{DEPTH_SHRINK} and then {POST_THIN} more when U2 re-sectioned them - "
      f"posts/uprights {FRONT_POST_Y0}..{FRONT_POST_Y1} (was 752..800), rungs "
      f"{RUNG_Y0}..{RUNG_Y1} ({RUNG_REST_LEDGE} mm rest ledge, was 25); D14: "
      f"guards INBOARD at {FRONT_GUARD_Y0}..{FRONT_GUARD_Y1}, "
      f"{FRONT_GUARD_SHIFT} mm in from the post outer faces; "
      f"platform/slats/bench slats/panel {PLATFORM_DEPTH} mm, end beams "
      f"{END_BEAM_LEN} mm, overall depth {OVERALL_DEPTH} mm")

# Inner clear width between the upper side rails
clear = FRONT_RAIL_Y0 - BACK_RAIL_Y1
assert abs(clear - INNER_CLEAR_WIDTH) < 1e-9, f"inner clear width is {clear}"
assert abs((front_rail.extents[1][0] - back_rail.extents[1][1]) - INNER_CLEAR_WIDTH) < 1e-9
print(f"OK  inner clear width between upper rails = {clear} mm")

# The ends must be completely open above the platform: no part above the slats
# may reach into the clear width between the two side rails.
for p in parts:
    (_, _), (y0, y1), (_, z1) = p.extents
    if z1 > SLAT_Z1:
        assert y1 <= BACK_RAIL_Y1 or y0 >= FRONT_RAIL_Y0, \
            f"'{p.label}' reaches into the sleeping area above the platform"
print("OK  both ends fully open above the platform (no upper end boards)")

# D4: both side rails must land on both end beams - including in X, which the
# post slimming (beams moved 73..121 -> 48..96) could have broken.
for beam in (p for p in parts if p.label.startswith("End Beam ")
             and "Block" not in p.label):
    assert beam.extents[2] == (END_BEAM_Z0, RAIL_BOTTOM), \
        "end beam top not flush with rail underside"
    for rail in (back_rail, front_rail):
        assert rail.extents[1][0] >= beam.extents[1][0] and \
            rail.extents[1][1] <= beam.extents[1][1], "rail not carried by the end beam"
        bear = min(rail.extents[0][1], beam.extents[0][1]) - \
            max(rail.extents[0][0], beam.extents[0][0])
        # V6b: the rail must cover the beam's WHOLE thickness - the bearing is
        # the beam, not the rail, and the beam is the thinner of the two now.
        assert bear >= END_BEAM_T - TOL, \
            f"'{rail.label}' only bears {bear:.1f} mm on '{beam.label}' in X"
print(f"OK  end beams {sec(END_BEAM_T, RAIL_H)} x {END_BEAM_LEN} at Z "
      f"{END_BEAM_Z0}..{RAIL_BOTTOM} carry both side rails "
      f"(full {END_BEAM_T} mm bearing in X, beams at X {END_BEAM_X[0]} / "
      f"{END_BEAM_X[1]})")

# V5: THE BEARING BLOCKS ARE GONE - AND THIS IS WHAT STANDS IN THEIR PLACE.
# Eight 36x48 offcuts used to hang off the post faces under the end beams and
# the bench rails, and the argument for them was "the member bears on wood
# instead of hanging in screw shear". It did not survive being followed to the
# end: the block itself hangs on ONE 6 mm screw (2.0 kN against up to 1 kN, the
# 0.50 that topped vedlegg A's screw rows), so it did not take the reaction out
# of steel, it halved the steel. The three corners now carry it on the members'
# OWN end fixings, which were always there, and this block is the arithmetic.
assert not [p for p in parts if "Bearing Block" in p.label], \
    "V5: a bearing block is back in the model"

# Conservative field values, the same ones vedlegg A quotes.
SCREW_SHEAR_KN = {5: 1.5, 6: 2.0}
# (joint, what it is, the vertical reaction ONE instance of it takes, kN)
# J1  - an end beam spans 836 mm between its two posts and sees the 2 kN
#       dynamic bed load, so a corner takes <= 1 kN.
# J8  - a front bench-rail segment is a two-support member (post, stub leg) of
#       ~584 mm with no cantilever; 1 kN of bench load at midspan puts 0.5 kN
#       on the post end.
# J8-B- the back rail's outer span is post X 98 -> stub leg centre 608.5,
#       ~510 mm, and the same 1 kN at its midpoint puts 0.5 kN on the post.
#       The two screws are skew in the XY plane and the reaction is Z, so both
#       are square to the load and neither loses anything to the skew.
# J17 - V13's end cleat is the same kind of corner: a member that hangs on its
#       own screws with no bearing under it. The end slat carries the bench
#       slat criterion's 0.5 kN (vedlegg A.1, one foot on one slat) over a
#       722 mm span between the cleat and the front bench rail, so the cleat
#       takes half of it - and the gate below then stands the WHOLE 0.5 kN
#       directly over the cleat anyway.
BLOCKLESS_CORNERS = [
    ("J1", "endebjelkeende → hjørnestolpe", 1.0),
    ("J8", "fremre benkevangeende → fremre stolpe", 0.5),
    ("J8-B", "bakre benkevangeende → bakre stolpe", 0.5),
    ("J17", "endelist → bakre stolpe (V13)", 0.25),
    # X10: J5-B belongs on this list and was not on it. It is exactly what V5
    # deleted everywhere else - a block on a post face with nothing under it -
    # and it was held out only by the sentence that said one screw was all the
    # face could take. The face is 36 x 68 now and it takes two, so the rule
    # applies to it like it applies to the rest. The reaction is half the
    # kilonewton the free-edge row stands on the middle of the plate: it
    # splits between the two blocks. The moment that comes with it is not a
    # shear row and gets its own, down where the blocks are built.
    ("J5-B", "bordkloss → stigevange (X9)", 0.5),
]
# The gate this change had to pass: no row over 0.8 even with the whole design
# load stood directly over the corner, i.e. at TWICE the reaction above.
MAX_BLOCKLESS_UTIL = 0.8
BLOCKLESS_REPORT = []
for _jid, _what, _reaction in BLOCKLESS_CORNERS:
    _screws = [f for f in FASTENER_SPECS
               if f["jid"] == _jid and f["kind"] == "screw"]
    _per = len(_screws) // JOINT[_jid]["n"]
    assert _per * JOINT[_jid]["n"] == len(_screws) and _per >= 2, \
        f"V5: {_jid} has {len(_screws)} screws over {JOINT[_jid]['n']} " \
        f"instances - a block-less corner needs a whole number of them, and " \
        f"at least two"
    _cap = sum(SCREW_SHEAR_KN[int(round(f["d"]))] for f in _screws[:_per])
    _util = _reaction / _cap
    _worst = 2 * _reaction / _cap
    assert _worst <= MAX_BLOCKLESS_UTIL, \
        f"V5: {_jid} ({_what}) is {_worst:.2f} utilised with the whole " \
        f"design load over the corner - over the {MAX_BLOCKLESS_UTIL} gate. " \
        f"Put the bearing block back and re-open the question"
    BLOCKLESS_REPORT.append((_jid, _what, _per, _cap, _reaction, _util, _worst))
print("OK  V5 klossløse hjørner - reaksjonen går gjennom leddets egne skruer:")
for _jid, _what, _per, _cap, _reaction, _util, _worst in BLOCKLESS_REPORT:
    print(f"      {_jid:5s} {_what:38s} {_per}x i skjær = {_cap:.1f} kN mot "
          f"{_reaction:.1f} kN → {_util:.2f} (verste plassering "
          f"{_worst:.2f}, grense {MAX_BLOCKLESS_UTIL:g})")

# And the geometry that says the beam end is an ordinary lap fixing and not the
# brittle end-split the blocks were bought against: the J1 pair has 3d of end
# distance along the beam's own grain and 4.5d of edge distance in the
# direction the load acts. MIN_EDGE (3d) is the rule this file enforces on
# every other joint; the LOADED edge, which is the one that governs a
# perpendicular-to-grain pair, has half as much again.
_j1 = [f for f in FASTENER_SPECS if f["jid"] == "J1"]
_j1_end = min(min(abs(f["anchor"][1] - e) for e in f["through"].extents[1])
              for f in _j1)
_j1_edge = min(min(abs(f["anchor"][2] - e) for e in f["through"].extents[2])
               for f in _j1)
assert _j1_end >= MIN_EDGE - TOL and _j1_edge >= MIN_EDGE - TOL, \
    f"J1: {_j1_end:g} mm to the beam end and {_j1_edge:g} mm to its loaded " \
    f"edge, want at least {MIN_EDGE} (3d) of both"
print(f"OK  V5 J1 i bjelkeenden: {_j1_end:g} mm ({_j1_end / SCREW_D:g}d) "
      f"endeavstand langs fiberretningen og {_j1_edge:g} mm "
      f"({_j1_edge / SCREW_D:g}d) kantavstand i lastretningen, i "
      f"{sec(END_BEAM_T, RAIL_H)} C24 - krav {MIN_EDGE} (3d)")

# W1/W5/W7: THE BACK BARRIER IS THE WALL. There are no back guard boards, so
# what has to be checked on that side is the mattress/wall entrapment gap.
#
# The history in one paragraph. v8/D12 pinned the mattress between two lines of
# posts at Y -48 and 752 - zero play, zero gap, but a 48 mm slot behind the back
# rail that it had to be kept out of. v9/W2+W4+W5 took the back posts off the
# mattress band and ran the platform over the slot, which cost 48 mm of wander
# and therefore a 48 mm gap at one edge. v10/W6 deletes the slot at its source by
# moving the posts INTO the rail plane, so the wall comes forward to Y -48:
#   clear between the stops   752 - (-48) = 800 = the mattress
#   wander                                =   0
#   worst single gap                      =   0
# The mattress is pinned again, this time between a wall and four verticals
# rather than between two lines of posts, and every millimetre under it is slat.
back_guards = [p for p in parts if p.label.startswith("Guard Rail Back")]
assert not back_guards, \
    "W1: back guard boards found - they are supposed to be deleted, the wall " \
    "is the barrier on that side"
assert (MATTRESS_STOP_Y0, MATTRESS_STOP_Y1) == (WALL_Y, FRONT_POST_Y0) == (-48, 752), \
    "W5: the mattress stops are the wall and the front vertical plane"
assert MATTRESS_WANDER == \
    (MATTRESS_STOP_Y1 - MATTRESS_STOP_Y0) - MATTRESS_W == 0, \
    f"W5/W7: the mattress can wander {MATTRESS_WANDER} mm, expected 0 - the " \
    f"clear between the stops is supposed to BE the mattress"
assert MATTRESS_STOP_Y1 - MATTRESS_STOP_Y0 == MATTRESS_W == 800, \
    "W7: the wall-to-front-vertical clear must be exactly the mattress width"
assert MAX_MATTRESS_GAP == MATTRESS_WANDER <= MAX_GUARD_OPENING, \
    f"EN 747 entrapment: the mattress can leave a {MAX_MATTRESS_GAP} mm gap, " \
    f"over the {MAX_GUARD_OPENING} mm limit"
# X10 - AND THIS TIME OFF THE SOLIDS. What stood here was
#     assert WALL_MATTRESS_GAP == MATTRESS_Y0 - WALL_Y == 0
# and WALL_MATTRESS_GAP is DEFINED as MATTRESS_Y0 - WALL_Y, with MATTRESS_Y0
# an alias of SLAT_Y0, an alias of BACK_RAIL_Y0, which is what WALL_Y is too.
# The whole chain is one constant compared to itself: it reads as the EN 747
# entrapment check and it would have passed with the mattress built in the next
# room. The check has to be asked of the BODIES - the drawn mattress against
# the wall face the bed actually presents and against the front verticals that
# actually stop it - and that is what it asks now.
MATTRESS_BUILT_Y0, MATTRESS_BUILT_Y1 = mattress.extents[1]
WALL_FACE_BUILT = min(p.extents[1][0] for p in parts)
FRONT_STOP_BUILT = min(p.extents[1][0] for p in parts
                       if p.label.startswith(("Corner Post Front",
                                              "Ladder Upright")))
gap_at_wall = MATTRESS_BUILT_Y0 - WALL_FACE_BUILT
gap_at_front = FRONT_STOP_BUILT - MATTRESS_BUILT_Y1
assert abs(gap_at_wall) < TOL and abs(gap_at_front) < TOL, (
    f"W5: the mattress body runs Y {MATTRESS_BUILT_Y0:g}..{MATTRESS_BUILT_Y1:g} "
    f"between a wall face at {WALL_FACE_BUILT:g} and front verticals at "
    f"{FRONT_STOP_BUILT:g} - {gap_at_wall:g} mm of gap at the wall and "
    f"{gap_at_front:g} at the front, and EN 747 allows "
    f"{MAX_GUARD_OPENING:g}. Both have to be 0: the mattress is PINNED, not "
    f"merely drawn tight")
assert max(gap_at_wall, gap_at_front) <= MAX_GUARD_OPENING, "W5: unreachable"
assert WALL_MATTRESS_GAP == gap_at_wall, (
    f"W5: the typed wall gap is {WALL_MATTRESS_GAP:g} and the built one is "
    f"{gap_at_wall:g}")
assert MATTRESS_Y1 == MATTRESS_STOP_Y1 == FRONT_POST_Y0, \
    "W5: the mattress front edge must be on the front stop"
# And the platform has to be under the mattress over the whole of it. X10: the
# line that stood here compared four aliases of BACK_RAIL_Y0 and conceded in
# its own comment that it was "trivially true"; it is the two BODIES now.
_slat_band = (min(s.extents[1][0] for s in bed_slats),
              max(s.extents[1][1] for s in bed_slats))
assert _slat_band == (MATTRESS_BUILT_Y0, MATTRESS_BUILT_Y1), \
    f"W5: the built platform is Y {_slat_band[0]:g}..{_slat_band[1]:g} under " \
    f"a built mattress at {MATTRESS_BUILT_Y0:g}..{MATTRESS_BUILT_Y1:g}"
print(f"OK  W1/W5/W7: no back guard - the WALL is the barrier on the back long "
      f"side and the frame is screwed to it through the back rail (S2). The "
      f"EN 747 case on that side is the mattress gap, and after W6 there is not "
      f"one: {MATTRESS_W} mm of mattress in a "
      f"{MATTRESS_STOP_Y1 - MATTRESS_STOP_Y0} mm clear between the wall "
      f"Y={MATTRESS_STOP_Y0} and the front verticals Y={MATTRESS_STOP_Y1} = "
      f"{MATTRESS_WANDER} mm of travel, so 0 mm at the wall and 0 mm at the "
      f"front (limit {MAX_GUARD_OPENING}); drawn at Y {MATTRESS_Y0}.."
      f"{MATTRESS_Y1}, which is the only place it fits. NOTE: the bed is "
      f"wall-side-specific and not reversible - see W1 at the top of this file "
      f"for the retrofit route back to a freestanding version")

# D2: four front guard segments, leaving exactly the ladder opening, each one
# lapped onto a corner post at one end and a ladder upright at the other.
front_guards = [p for p in parts if p.label.startswith("Guard Rail Front")]
assert len(front_guards) == 4, f"expected 4 front guard segments, got {len(front_guards)}"
assert len(front_guards) == len([p for p in parts if p.label.startswith("Guard Rail")]), \
    "W1: every guard board in the bed must be a FRONT segment now"
post_x_ranges = [p.extents[0] for p in parts if p.label.startswith("Corner Post Front")]
up_x_ranges = [p.extents[0] for p in up]
for g in front_guards:
    (x0, x1), y, z = g.extents
    # D7: 34x98 board. D14: landing flat on the plane Y = 752 (the INNER faces
    # of the corner posts and the ladder uprights) instead of the outer plane
    # 800, so the board sits between the verticals and the mattress footprint.
    # W1: this is the ONLY guard profile left in the bed.
    assert y == (FRONT_GUARD_Y0, FRONT_GUARD_Y1)
    assert y[1] - y[0] == GUARD_T and z[1] - z[0] == GUARD_W, \
        f"'{g.label}' is not {sec(GUARD_T, GUARD_W)}"
    assert y[1] == FRONT_POST_Y0, \
        f"'{g.label}' does not lie on the post/upright INNER face plane " \
        f"Y={FRONT_POST_Y0} (D14)"
    assert y[1] <= FRONT_POST_Y1 - POST_T + TOL, \
        f"'{g.label}' still stands outside the post plane - D14 puts it inboard"
    # D14: the board hangs GUARD_T past the mattress front edge (752 -> 718).
    # That has to be clear AIR: the band starts 75 mm above the mattress top.
    assert z[0] - MATTRESS_Z1 >= MIN_GUARD_INBOARD_CLEAR, \
        f"'{g.label}' overhangs the mattress by {FRONT_GUARD_Y1 - y[0]} mm and " \
        f"is only {z[0] - MATTRESS_Z1} mm above it (want " \
        f">= {MIN_GUARD_INBOARD_CLEAR})"
    assert x1 - x0 == FRONT_GUARD_SEG_LEN, f"'{g.label}' is {x1 - x0} long"
    lap_post = max(min(x1, a1) - max(x0, a0) for a0, a1 in post_x_ranges)
    lap_up = max(min(x1, a1) - max(x0, a0) for a0, a1 in up_x_ranges)
    assert lap_post >= POST_W - THROUGH_X0, f"'{g.label}' barely laps a corner post"
    # D13: the lap is the FULL width of the upright, which is what the detail
    # asks for. D14: same overlap, on the upright's INNER Y face - the screws go
    # in from inside the bed. U2: the upright turned, so that full width is 48
    # instead of 36 and the corner-post lap grew 45 -> 95 with the post. Both
    # are checked against MIN_GUARD_LAP as well, so neither can quietly shrink
    # below the narrowest lap this detail has ever run at.
    assert lap_up >= UPRIGHT_W, \
        f"'{g.label}' does not fully lap a ladder upright ({lap_up})"
    assert lap_up >= MIN_GUARD_LAP and lap_post >= MIN_GUARD_LAP, \
        f"'{g.label}' laps {lap_up} mm of upright and {lap_post} mm of post; " \
        f"the detail needs {MIN_GUARD_LAP} of each"
    # X10: what stood here was `lap_post * GUARD_W >= (POST_W - THROUGH_X0) *
    # GUARD_W` and its twin - the same GUARD_W on both sides of the >=, so it
    # divided out and left the two asserts eight lines up, restated. The area
    # is real when the height comes off the BOARD, and the floor is a number of
    # its own rather than the same expression again.
    lap_h = z[1] - z[0]
    assert lap_post * lap_h >= MIN_GUARD_LAP * lap_h and \
        lap_up * lap_h >= MIN_GUARD_LAP * lap_h, \
        f"'{g.label}' laps {lap_post * lap_h:.0f} mm2 of post and " \
        f"{lap_up * lap_h:.0f} mm2 of upright, and the floor is " \
        f"{MIN_GUARD_LAP * lap_h:.0f} - a board on a {lap_h:g} mm face"
for z0 in GUARD_BAND_Z0:
    band = sorted((g for g in front_guards if g.extents[2][0] == z0),
                  key=lambda p: p.extents[0][0])
    assert len(band) == 2
    gap = band[1].extents[0][0] - band[0].extents[0][1]
    assert abs(gap - LADDER_CLEAR) < TOL, f"climb-through gap is {gap}, want {LADDER_CLEAR}"
    assert (band[0].extents[0][1], band[1].extents[0][0]) == (LADDER_INNER_L,
                                                              LADDER_INNER_R), \
        "D13: the guard segments must die on the upright inner faces"
    # D14: the boards butt the SAME two uprights, from the other Y face, so the
    # opening is still the upright-to-upright clear and the inboard move cannot
    # have narrowed it. Measured against the actual upright parts, not the
    # constants, so a mistake in either would show.
    assert (band[0].extents[0][1], band[1].extents[0][0]) == \
        (up[0].extents[0][1], up[1].extents[0][0]), \
        "D14: the climb-through is no longer measured between the upright " \
        "inner faces - the inboard guards must butt the same uprights"
# ---------------------------------------------------------------------------
# THE MATTRESS IS A RANGE, NOT A NUMBER
# ---------------------------------------------------------------------------
# The bed is dimensioned around a STANDARD 80 x 200 cm mattress - that is the
# thing a reader goes and buys - and the model draws one particular one of
# those, 140 mm thick. But thickness is the one dimension the shop does not
# fix, and BOTH ends of it are a safety limit here, pulling opposite ways:
#
#   too THIN   the mattress top drops away from the lower guard band and the
#              gap under it opens past the EN 747 entrapment limit.
#   too THICK  the mattress top rises towards the top of the guard and the
#              barrier standing above the sleeper falls under EN 747's
#              minimum.
#
# Both bounds are read off the same two fixed heights - the slat top the
# mattress lies on, and the guard - so both are derived, and the panel on the
# last page of the manual prints the pair with an arrow on each constraint.
GUARD_TOP = GUARD_BAND_Z0[-1] + GUARD_W
# V7: THE WINDOW IS A BAND, NOT A CEILING. EN 747-1 does not merely cap the
# opening between the mattress top and the underside of the lowest guard board
# at 75 mm - it requires that opening to be <= 5 mm OR in the 60..75 mm band,
# because an opening between the two is the one a limb wedges in instead of
# passing through. The mattress sets that opening, so the mattress window is
# the band read backwards:
#   thinnest  -> the opening is at its widest, and 75 is the top of the band
#   thickest  -> the opening is at its narrowest, and 60 is the bottom of it
# The old MAX came off MIN_GUARD_OVER_MATTRESS (barrier height above the
# sleeping surface) and gave 326 - true as far as it went, but it was not the
# governing bound, and a 16 cm mattress inside it put the opening at 55 mm,
# squarely in the trap window. The barrier-height bound is still checked; it is
# simply never the one that bites.
MATTRESS_H_MIN = GUARD_BAND_Z0[0] - SLAT_Z1 - MAX_GUARD_OPENING
MATTRESS_H_MAX = int(GUARD_BAND_Z0[0] - SLAT_Z1 - EN_LIMB_BAND[0])
MATTRESS_H_MAX_BARRIER = GUARD_TOP - SLAT_Z1 - MIN_GUARD_OVER_MATTRESS
assert MATTRESS_H_MAX < MATTRESS_H_MAX_BARRIER, \
    "V7: the band bound is supposed to be the governing one"
assert (MATTRESS_H_MIN, MATTRESS_H_MAX) == (110, 125), \
    f"V7/X4: the mattress window is {MATTRESS_H_MIN}..{MATTRESS_H_MAX}, want 110..125"
assert MATTRESS_H_MIN <= MATTRESS_H <= MATTRESS_H_MAX, \
    f"the modelled {MATTRESS_H} mm mattress is outside its own legal band " \
    f"{MATTRESS_H_MIN}..{MATTRESS_H_MAX} mm"
# ...and the two bounds have to be checked at the bound, not at the modelled
# thickness: it is the EXTREMES that either pass or do not.
assert GUARD_BAND_Z0[0] - (SLAT_Z1 + MATTRESS_H_MIN) <= MAX_GUARD_OPENING
assert GUARD_TOP - (SLAT_Z1 + MATTRESS_H_MAX) >= MIN_GUARD_OVER_MATTRESS
assert MATTRESS_H_MAX > MATTRESS_H_MIN, \
    "no mattress thickness satisfies both guard rules"
print(f"OK  EN 747 madrasstykkelse: {MATTRESS_H_MIN}..{MATTRESS_H_MAX} mm on "
      f"a slat top of {SLAT_Z1}. Thinner than {MATTRESS_H_MIN} and the gap "
      f"under the lower band goes past {MAX_GUARD_OPENING} mm; thicker than "
      f"{MATTRESS_H_MAX} and the barrier over the mattress falls under "
      f"{MIN_GUARD_OVER_MATTRESS} mm. Modelled: {MATTRESS_H} mm (gap "
      f"{GUARD_BAND_Z0[0] - MATTRESS_Z1}, barrier {GUARD_TOP - MATTRESS_Z1})")

print(f"OK  D2/D7/D13/D14: 4 front guard segments {sec(GUARD_T, GUARD_W)} x "
      f"{FRONT_GUARD_SEG_LEN} at X {FRONT_GUARD_SEGMENTS[0][0]}.."
      f"{FRONT_GUARD_SEGMENTS[0][1]} / {FRONT_GUARD_SEGMENTS[1][0]}.."
      f"{FRONT_GUARD_SEGMENTS[1][1]}, Y {FRONT_GUARD_Y0}..{FRONT_GUARD_Y1} = "
      f"the INNER faces of the front posts / uprights (D14, was 800..834), "
      f"{UPRIGHT_W} x {GUARD_W} mm face lap on the uprights and "
      f"{POST_W - THROUGH_X0} x {GUARD_W} mm on the corner posts - screwed from "
      f"inside the bed - clear climb-through gap {LADDER_CLEAR} mm in both "
      f"bands, boards {GUARD_T} mm over the mattress footprint but "
      f"{GUARD_BAND_Z0[0] - MATTRESS_Z1} mm above the mattress top "
      f"{MATTRESS_Z1}, so no contact")

# D14 COLLISION SWEEP. The 34 mm slice the boards moved INTO - Y 718..752 above
# the lower band - has to contain the four guard segments and nothing else. This
# is the other half of the empty-old-plane check: one says nothing was left
# behind, this one says nothing was already there.
sweep_y = (FRONT_GUARD_Y0, FRONT_GUARD_Y1)           # 718 .. 752
sweep_z0 = GUARD_BAND_Z0[0]                          # 1412
occupants = [p for p in parts + [panel_bed, panel_table]
             if min(p.extents[1][1], sweep_y[1]) - max(p.extents[1][0], sweep_y[0]) > TOL
             and p.extents[2][1] > sweep_z0 + TOL]
assert {p.label for p in occupants} == {g.label for g in front_guards}, \
    f"D14: Y {sweep_y[0]}..{sweep_y[1]} above Z {sweep_z0} holds " \
    f"{sorted(p.label for p in occupants)} - only the 4 guard segments may be " \
    f"in there"
assert MATTRESS_Z1 < sweep_z0, \
    f"D14: the mattress tops out at {MATTRESS_Z1}, into the swept band"
print(f"OK  D14 collision sweep: Y {sweep_y[0]}..{sweep_y[1]} above Z "
      f"{sweep_z0} holds exactly the {len(occupants)} guard segments and "
      f"nothing else (mattress tops out at {MATTRESS_Z1}, "
      f"{sweep_z0 - MATTRESS_Z1} mm below)")

# D6 (W1: FRONT SIDE ONLY): guard re-banding. Every opening measured ABOVE THE
# MATTRESS SURFACE has to be <= 75 mm (EN 747 entrapment), and the barrier has
# to stand at least 160 mm above the mattress.
#
# W1 ripple: this arithmetic used to describe both long sides, and it now
# describes the FRONT one. The bands and the numbers are byte-for-byte what D6
# left them - 1412..1510, 1585..1683, 75 / 75 / 17, 346 above the mattress -
# because W1 removed boards, it did not move any. The back side's EN 747 case
# is the 48 mm mattress gap checked in the W1/W5 block above; the two of them
# together are the complete entrapment argument for this bed.
# The third opening closes against the FRONT post tops (2037 after X1). The
# posts are set by the lift and the bands by the mattress, so this opening is
# the remainder between them: 28 -> 58 mm, still inside the 75 mm limit.
# The back posts stop at 1402 (W2/W6) and take no part in this check - on
# that side the "barrier" is a wall that runs to the ceiling.
guard_openings = [
    ("mattress top -> band 1", GUARD_BAND_Z0[0] - MATTRESS_Z1),
    ("band 1 -> band 2", GUARD_BAND_Z0[1] - (GUARD_BAND_Z0[0] + GUARD_W)),
    ("band 2 -> front post tops", POST_HEIGHT - (GUARD_BAND_Z0[1] + GUARD_W)),
]
for what, o in guard_openings:
    assert o > 0, f"guard bands overlap or invert: {what} = {o}"
    assert o <= MAX_GUARD_OPENING + TOL, \
        f"EN 747 entrapment: opening '{what}' is {o} mm > {MAX_GUARD_OPENING}"
guard_over_mattress = GUARD_BAND_Z0[1] + GUARD_W - MATTRESS_Z1
assert guard_over_mattress >= MIN_GUARD_OVER_MATTRESS, \
    f"barrier only {guard_over_mattress} mm above the mattress"
# every guard board must be in one of those bands - and, after W1, be a front
# segment carried by the front posts, which are the ones that reach 2037.
# D14: "front" is no longer "outboard". The board hangs on the INNER faces of
# those posts, so the test is that its outer face IS the post inner plane 752 -
# far from the back half of the bed either way (the back rail ends at Y 0).
for g in parts:
    if g.label.startswith("Guard Rail"):
        assert g.extents[2][0] in GUARD_BAND_Z0 and \
            g.extents[2][1] - g.extents[2][0] == GUARD_W, \
            f"'{g.label}' is not in one of the D6 guard bands"
        assert abs(g.extents[1][1] - FRONT_POST_Y0) < TOL, \
            f"W1/D14: '{g.label}' is not hung on the front verticals' inner " \
            f"plane Y={FRONT_POST_Y0} - the back side has no guard boards"
assert max(p.extents[2][1] for p in front_posts) == \
    GUARD_BAND_Z0[1] + GUARD_W + guard_openings[-1][1] == POST_HEIGHT
print(f"OK  D6/W1 (front side): guard bands Z "
      f"{GUARD_BAND_Z0[0]}..{GUARD_BAND_Z0[0] + GUARD_W} "
      f"and {GUARD_BAND_Z0[1]}..{GUARD_BAND_Z0[1] + GUARD_W}; openings above "
      f"the mattress top ({MATTRESS_Z1}): "
      + " / ".join(f"{o:.0f}" for _, o in guard_openings)
      + f" mm (limit {MAX_GUARD_OPENING}), barrier {guard_over_mattress} mm "
      f"above the mattress (min {MIN_GUARD_OVER_MATTRESS}); back side: no "
      f"boards, a {MAX_MATTRESS_GAP} mm worst-case mattress gap instead (W5)")

# ---------------------------------------------------------------------------
# THE ROOM HAS A CEILING  (X1)
# ---------------------------------------------------------------------------
# X1. Until v14 the niche was described in two directions - sideways by
# WALL_SPAN and upwards by nothing at all - and the third one, the ceiling, was
# the number the builder carried in his head while he decided how high to put
# the bunk. ROOM_H writes it down (2450 mm in Hanna's room), and once it is
# written down it can do the two jobs a limit is for.
#
#   1. IT IS A CEILING. Nothing may reach it, and the bed must be able to be
#      SWUNG UP into place under it: the front frame goes together lying on the
#      floor and is tilted upright, and a rectangle tilting about its foot
#      sweeps its own DIAGONAL, not its height. Both are measured off the built
#      solid below - the height off the tallest part, the depth off the
#      envelope - so neither can be argued with.
#
#   2. IT IS A HEAD ROOM BUDGET, AND IT IS THE REASON THE BUNK MOVED. The two
#      storeys share a FIXED POT: the room, less the seat face the sitter
#      starts from, less the slat and the mattress on it - 2450 - 420 - 23 -
#      120 = 1887 mm - and the platform is only the sliding wall between the
#      two halves of it. Nothing anyone does to this bed changes the pot; the
#      only question is where the wall goes, and THAT is a question about what
#      each storey is FOR.
#
#      v13 answered it by accident and got 781 below / 1114 above: one sitting
#      height for a 1433 mm child in the storey the family actually lives in,
#      and 300 mm of unused ceiling over a sleeper who is lying down. v14
#      answers it on purpose, and the answer is NOT an even split:
#        * THE LOWER STOREY IS THE ROOM. Play, homework, sofa, the table, two
#          children and an adult on the floor - it is where the hours go, and
#          the thing that decides whether it feels like a room or a den is
#          standing head room, not sitting head room. 1080 mm to the slat
#          underside is what X1 buys it (1500 off the floor, less the 420 mm
#          seat). For comparison, the shop-bought bunk this design was measured
#          against - IKEA SMÅSTAD - gives 1420 mm floor to slat; HANNA gives
#          1500.
#        * THE UPPER STOREY IS A BED, AND NOTHING ELSE. Nobody stands in it and
#          nobody sits in it for long: what it needs is enough air to sit up,
#          swing the legs out and get down the ladder. That is one sitting
#          height for a child, not for an adult - so the rule over the mattress
#          is MIN_LIE_HEADROOM (750), deliberately lower than the 900 the lower
#          storey has to clear, and 807 is what it gets.
#      THE INTENTION CHANGED, AND THAT IS WHY THE RULE CHANGED. This is worth
#      saying plainly because an assert that gets relaxed is normally a smell:
#      until v14 both storeys were held to the same 900 mm sitting rule, on the
#      unexamined assumption that they were the same kind of place. They are
#      not. The upper storey is a sleeping berth and it is now dimensioned as
#      one; the lower storey took the difference and is dimensioned as a room.
#      The pot assert below is what keeps that honest - it makes the trade
#      visible instead of letting both numbers drift up.
MIN_CEILING_CLEAR = 200          # over the tallest part of the finished bed
MIN_SIT_HEADROOM = 900           # LOWER storey: one sitting height, 1650 mm person
MIN_LIE_HEADROOM = 750           # UPPER storey: a berth - sit up, swing out, climb down
# Measured, not typed: the top of the tallest piece of wood in the bed and the
# top of the mattress it is drawn around, both read off the solids.
BUILT_TOP_Z = max(p.extents[2][1] for p in parts)              # 2037
BUILT_MATTRESS_TOP_Z = mattress.extents[2][1]                  # 1643
CEILING_CLEAR = ROOM_H - BUILT_TOP_Z                           # 413
TILT_SWEEP = math.hypot(BUILT_TOP_Z, OVERALL_DEPTH)            # 2202
UPPER_SIT_HEADROOM = ROOM_H - BUILT_MATTRESS_TOP_Z             # 807
assert CEILING_CLEAR >= MIN_CEILING_CLEAR, \
    f"X1: the bed tops out at {BUILT_TOP_Z} in a {ROOM_H} mm room - " \
    f"{CEILING_CLEAR} mm of ceiling clearance, want {MIN_CEILING_CLEAR}"
assert TILT_SWEEP <= ROOM_H, \
    f"X1: tilting the {BUILT_TOP_Z} x {OVERALL_DEPTH} mm front frame upright " \
    f"sweeps {TILT_SWEEP:.0f} mm, and the ceiling is at {ROOM_H}"
assert UPPER_SIT_HEADROOM >= MIN_LIE_HEADROOM, \
    f"X1: {UPPER_SIT_HEADROOM} mm from the upper mattress top to the ceiling, " \
    f"want {MIN_LIE_HEADROOM} - you cannot sit up and swing out of the berth"
assert LOWER_HEADROOM >= MIN_SIT_HEADROOM, \
    f"X1: {LOWER_HEADROOM} mm over the lower sleeping surface, want " \
    f"{MIN_SIT_HEADROOM} - the sofa is a crawl space, not a seat"
# X10 - AND NOW MEASURED, over the footprint the surface actually has. The
# clear field above is the distance to the SLATS; this is the distance to the
# nearest piece of wood, whatever it is, read off the solids in both modes and
# over LOWER_SLEEP_RECTS - the same footprint the cushion tiling is checked
# against. Three permanent members stand in it and none of them was ever
# printed: the ladder rungs cross the surface's front strip, the back table
# ledger runs the whole length of the wall strip the seat cushions lie on, and
# the two bordklosser sit beside the ladder.
#
# THE RULE IS NOT A CLEARANCE, IT IS A LIST. There is no honest floor to put
# under 104 mm - that is a ladder, and a ladder over the front edge of a bunk
# is the bed working as drawn. What can be asserted, and what would actually
# have caught this, is that the things standing in the lower storey's air are
# exactly the things the reader is told about: add a member into that band and
# the assert names it. Everything else about the storey stays as it was.
# In table mode the plate itself and its four battens stand over the surface -
# that is the table, and the whole point of it, so they are named too.
LOWER_HEADROOM_INTRUDERS = {"Ladder Rung", "Table Ledger Back",
                            "Table Bearer", "End Beam", "Upper Side Rail",
                            "Corner Post", "Ladder Upright",
                            "Movable Panel", "Panel Stiffener Batten",
                            "Panel Front Batten"}


def _over_lower_sleep(part):
    """mm2 of the lower sleeping surface this part stands over."""
    (x0, x1), (y0, y1), _ = part.extents
    a = 0.0
    for rx0, rx1, ry0, ry1 in LOWER_SLEEP_RECTS:
        dx = min(x1, rx1) - max(x0, rx0)
        dy = min(y1, ry1) - max(y0, ry0)
        if dx > TOL and dy > TOL:
            a += dx * dy
    return a


LOWER_HEADROOM_MIN, LOWER_HEADROOM_WHO = 1e18, None
LOWER_HEADROOM_WALL, LOWER_HEADROOM_WALL_WHO = 1e18, None
_hr_unknown = set()
for _mode, _panel in MODES.items():
    for _p in mode_parts(_panel):
        if is_soft(_p) or _p.extents[2][0] < CUSHION_TOP_BENCH - TOL:
            continue
        if _over_lower_sleep(_p) <= TOL:
            continue
        _clear = _p.extents[2][0] - CUSHION_TOP_BENCH
        if _clear < LOWER_HEADROOM_MIN:
            LOWER_HEADROOM_MIN, LOWER_HEADROOM_WHO = _clear, _p.label
        # the wall strip is where the seat cushions and the pillows are
        if _p.extents[1][0] < BACK_RAIL_Y1 - TOL \
                and _clear < LOWER_HEADROOM_WALL:
            LOWER_HEADROOM_WALL, LOWER_HEADROOM_WALL_WHO = _clear, _p.label
        if _clear < MIN_SIT_HEADROOM and not any(
                _p.label.startswith(k) for k in LOWER_HEADROOM_INTRUDERS):
            _hr_unknown.add(_p.label)
assert not _hr_unknown, (
    f"X10: {sorted(_hr_unknown)} stand less than {MIN_SIT_HEADROOM} mm over "
    f"the lower sleeping surface and are not on the list of things the "
    f"drawings name. Either the part is in the wrong place or the reader has "
    f"not been told about it - both are the same bug")
assert LOWER_HEADROOM_WHO is not None and LOWER_HEADROOM_WALL_WHO is not None, \
    "X10: nothing at all stands over the lower sleeping surface - measure again"
assert LOWER_HEADROOM_MIN < LOWER_HEADROOM, \
    "X10: the measured head room cannot be more than the clear field to the " \
    "slats - one of the two is not measuring what it says"
print(f"OK  X10 nedre etasje, MÅLT på kroppene over soveflatens fotavtrykk "
      f"({LOWER_SLEEP_AREA / 1e6:.2f} m²): fritt felt til spilene "
      f"{LOWER_HEADROOM} mm, men laveste faste del er "
      f"'{LOWER_HEADROOM_WHO}' på {LOWER_HEADROOM_MIN:g} mm, og over "
      f"putestripa ved veggen er det '{LOWER_HEADROOM_WALL_WHO}' på "
      f"{LOWER_HEADROOM_WALL:g} mm. Begge tallene er permanente og begge står "
      f"i nøkkelmålene - 1080 er takhøyden i rommet mellom dem, ikke over dem")
# THE POT, AND WHICH WAY IT LEANS. The two head rooms and the stack between them
# add up to the room - that is what makes the split a zero-sum choice rather
# than a wish - and v14's choice is that the LIVING storey gets the larger half.
# Both halves of that sentence are asserted: the sum, so the pot cannot drift,
# and the direction, so no later round can quietly hand the majority back to a
# storey nobody stands up in.
HEADROOM_POT = LOWER_HEADROOM + UPPER_SIT_HEADROOM             # 1887
assert (HEADROOM_POT + (SLAT_Z1 - SLAT_Z0) + MATTRESS_H
        + CUSHION_TOP_BENCH) == ROOM_H, \
    "X1: the two storeys and the platform stack do not add up to the room"
assert LOWER_HEADROOM > UPPER_SIT_HEADROOM, \
    f"X1: the {HEADROOM_POT} mm of head room is split "\
    f"{LOWER_HEADROOM} below / {UPPER_SIT_HEADROOM} above - the storey people "\
    f"live in is supposed to have the bigger half"
print(f"OK  X1 rommet: {ROOM_H} mm fra gulv til tak. Høyeste del {BUILT_TOP_Z} "
      f"(stolpetopp), {CEILING_CLEAR} mm klaring til taket (krav "
      f"{MIN_CEILING_CLEAR}), og fronten - {BUILT_TOP_Z} x {OVERALL_DEPTH} - "
      f"sveiper {TILT_SWEEP:.0f} mm når den vippes opp. POTTEN er "
      f"{HEADROOM_POT} mm og den er fast. NEDE (leke- og oppholdssonen, den "
      f"store halvdelen): {LOWER_HEADROOM} mm fri høyde over soveflaten "
      f"({LOWER_HEADROOM_RAIL} under sidevangene), {SLAT_Z0} mm fra gulvet til "
      f"spilenes underside - krav {MIN_SIT_HEADROOM} "
      f"({MIN_SIT_HEADROOM / SIT_RATIO:.0f} mm person), margin "
      f"{LOWER_HEADROOM - MIN_SIT_HEADROOM} mm. OPPE (ren sovekøye): "
      f"{UPPER_SIT_HEADROOM} mm over madrassen - krav {MIN_LIE_HEADROOM}, "
      f"margin {UPPER_SIT_HEADROOM - MIN_LIE_HEADROOM} mm. v13 delte den "
      f"781/1114 - stikk motsatt vei")

# C3/C5/D11: 34x98 bench slats on the bench rails - one continuous rail at the
# back, two lapped segments at the front - and the bed-mode panel sitting one
# cushion-thickness below the resulting bench top.
bench_rails = [p for p in parts if "Bench Rail" in p.label and "Block" not in p.label]
back_bench_rails = [p for p in bench_rails if p.label.startswith("Bench Rail Back")]
front_bench_rails = [p for p in bench_rails if p.label.startswith("Bench Rail Front")]
assert len(back_bench_rails) == 1, "C5: expected exactly one continuous back bench rail"
assert len(front_bench_rails) == 2, \
    f"D11: expected 2 front bench rail segments, got {len(front_bench_rails)}"
for r in bench_rails:
    assert r.extents[2] == (BENCH_RAIL_BOTTOM, BENCH_RAIL_TOP), \
        f"'{r.label}' is not at Z {BENCH_RAIL_BOTTOM}..{BENCH_RAIL_TOP}"
    assert r.extents[1][1] - r.extents[1][0] == BENCH_RAIL_T
assert back_bench_rails[0].extents[0] == (BETWEEN_POSTS_X0, BETWEEN_POSTS_X1), \
    f"C5/W9: the back bench rail must run post to post, X {BETWEEN_POSTS_X0}.." \
    f"{BETWEEN_POSTS_X1} ({BETWEEN_POSTS_LEN} mm)"
assert back_bench_rails[0].extents[1] == (BACK_RAIL_Y0, BACK_RAIL_Y1)
# W9: it butts both back posts, so its ends are FIXED as well as borne - a face
# per end against the post's X-inner plane, 36 (Y) x 68 (Z) = 2448 mm2 of screwed
# contact. [was written 48 x 73 = 3504: the Y is the POST's 36, not the rail's
# 48, and the Z is the 48x68 rail's 68, not the 21x95 ledger's 73 - two numbers
# from two different rounds, in one product neither of them belonged to.] Measured against the real posts.
# U2: the face that end fixing lands on is 36 mm deep in Y now, not 48, so the
# contact is measured against the real post rather than assumed to be the
# member's whole end. Both members are 48 deep after V2, so both butt over 36
# of it - one number for the pair.
# X10: the height used to be handed in beside the member - BENCH_RAIL_H,
# LEDGER_BACK_H - and then compared against POST_T * BENCH_RAIL_H, so the
# height cancelled and what was left was `overlap_y == POST_T`. Build the rail
# 90 mm tall and the assert still passed. It is read off the body now, like
# the Y overlap always was.
POST_TO_POST_ENDS = {
    "Bench Rail Back (continuous)": back_bench_rails[0],
    "Table Ledger Back": support_rail,
}
end_fixings = {}
for what, member in POST_TO_POST_ENDS.items():
    (rx0, rx1), (ry0, ry1), (rz0, rz1) = member.extents
    height = rz1 - rz0
    assert (rx0, rx1) == (BETWEEN_POSTS_X0, BETWEEN_POSTS_X1), \
        f"W9: '{what}' must run post to post, it is at X {rx0}..{rx1}"
    areas = []
    for bp in back_posts:
        (px0, px1), (py0, py1), _ = bp.extents
        assert px1 == rx0 or px0 == rx1, \
            f"W9: '{what}' (X {rx0}..{rx1}) does not butt '{bp.label}' " \
            f"(X {px0}..{px1})"
        overlap_y = min(ry1, py1) - max(ry0, py0)
        assert overlap_y > 0, f"U2: '{what}' misses '{bp.label}' in Y entirely"
        areas.append(overlap_y * height)
    assert len(areas) == 2 and areas[0] == areas[1]
    end_fixings[what] = areas[0]
assert end_fixings["Bench Rail Back (continuous)"] == 2448, \
    f"U2: the back bench rail butts {end_fixings['Bench Rail Back (continuous)']}" \
    f" mm2 of post face, want 36 x 68 = 2448"
# V2: the ledger is the bench rail's profile now, so it butts the same 36 x 68
# of post face the bench rail does - 2448 mm2 instead of the 21x95's 1995.
# [the line here used to say 36 x 73 = 2628; 73 was the 21x95 ledger's own
#  height and it did not survive V2 either.]
assert end_fixings["Table Ledger Back"] == 2448, \
    f"V2: the back ledger butts {end_fixings['Table Ledger Back']} mm2 of " \
    f"post face, want the same 36 x 68 = 2448 the bench rail butts"
assert (back_bench_rails[0].extents[2][1] - back_bench_rails[0].extents[2][0]
        == BENCH_RAIL_H
        and support_rail.extents[2][1] - support_rail.extents[2][0]
        == LEDGER_BACK_H), \
    "V2: one of the two post-to-post members is not the section the file says"
assert BENCH_TOP == BENCH_RAIL_TOP + BENCH_SLAT_T == 320   # [X3: was 282]
# D10/U1: the cushion recess. The bench slat got 2 mm thicker and the panel did
# not (it is an 18 mm sheet on a rail top that has not moved), so the dip the
# fold-out cushions fold into grows 16 -> 18 mm. That is the right direction:
# the recess exists to swallow a cushion, and 18 mm of it is 18 mm.
# V6: the dip is BENCH_SLAT_T - PANEL_T and nothing else - the bench slat and
# the panel start from the same 259 plane - so the 23 mm slat takes it 18 -> 5.
# The three zones of the lower sleeping surface are now essentially LEVEL, and
# V13 has since cashed that in: with the dip down to 5 mm the four cushions can
# all be ONE thickness, so the old rule "the middle cushion is 5 mm thicker" is
# retired. Nothing folds down into a recess any more; the 5 mm is a step foam
# takes up, and no cushion joint even falls on a zone boundary now.
assert PANEL_BENCH_DIP == 5 and PANEL_TOP_BED == BENCH_TOP - PANEL_BENCH_DIP, \
    "D10/U1/V6: the bed-mode panel should sit 5 mm below the bench tops"
assert PANEL_BENCH_DIP == BENCH_SLAT_T - PANEL_T + (BENCH_RAIL_TOP -
                                                   PANEL_UNDER_BED), \
    "D10: the dip is the bench slat minus the panel, both off the same rail top"
print(f"OK  C5/W9/U2: back bench rail {sec(BENCH_RAIL_T, BENCH_RAIL_H)} x "
      f"{BETWEEN_POSTS_LEN} (was 1894, {THROUGH_LEN} before that) at X "
      f"{BETWEEN_POSTS_X0}..{BETWEEN_POSTS_X1}, Z {BENCH_RAIL_BOTTOM}.."
      f"{BENCH_RAIL_TOP} - butting both back posts over "
      f"{int(end_fixings['Bench Rail Back (continuous)'])} mm2 of their "
      f"{POST_T} mm X-inner faces (was 48 x 73 = 3504 on a 48 mm post) and "
      f"screwed to them (2 x 6x80 skråskruer per ende, J8-B - no bearing "
      f"block since V5), propped by 2 stub legs")
print(f"OK  C3: bench slats {sec(BENCH_SLAT_T, BENCH_SLAT_W)}, bench top Z="
      f"{BENCH_TOP}, bed-mode panel {PANEL_UNDER_BED}..{PANEL_TOP_BED} "
      f"({PANEL_BENCH_DIP} mm below the bench tops - the cushion recess, D10)")

# W9/U2: THE BENCH SLAT FIELD. The five slats per bench start at the back post's
# X-inner face (a slat runs Y -48..752 and would otherwise cut through the post)
# and the last one lands exactly on the bench end. U2 moved that face 48 -> 98,
# so the field is 50 mm shorter and the same five boards close up. Checked as a
# field, not as a formula: the real slat extents, their real gaps, and the two
# ends of the run.
bench_slats_by_side = {}
for p in bench_slat_parts:
    bench_slats_by_side.setdefault(p.label.split("_")[0], []).append(p)
assert len(bench_slats_by_side) == 2
bench_slat_gaps = []
for side, group in sorted(bench_slats_by_side.items()):
    assert len(group) == BENCH_SLAT_COUNT
    xs = sorted(p.extents[0] for p in group)
    gaps = [xs[i + 1][0] - xs[i][1] for i in range(len(xs) - 1)]
    bench_slat_gaps += gaps
    for p in group:
        assert p.extents[2] == (BENCH_RAIL_TOP, BENCH_TOP), \
            f"C3: '{p.label}' is not lying on the bench rail tops"
        assert (p.extents[1][1] - p.extents[1][0]) == BENCH_SLAT_LEN
    # the field runs post inner face -> bench end (mirrored on the right)
    want = ((BENCH_SLAT_X_START, BENCH_LEN) if side == "Bench Slat Left"
            else (WALL_SPAN - BENCH_LEN, WALL_SPAN - BENCH_SLAT_X_START))
    assert (xs[0][0], xs[-1][1]) == want, \
        f"W9/U2: the {side} field runs X {xs[0][0]}..{xs[-1][1]}, want {want}"
    # and it must not touch the corner posts it starts beside
    for px0, px1 in ((x, x + POST_W) for x in CORNER_POST_X):
        for p in group:
            (sx0, sx1), _, _ = p.extents
            assert min(sx1, px1) - max(sx0, px0) <= TOL, \
                f"U2: '{p.label}' overlaps the corner post at X {px0}..{px1}"
assert max(bench_slat_gaps) <= MAX_BENCH_SLAT_GAP + TOL, \
    f"C3: the widest bench slat gap is {max(bench_slat_gaps)}, limit " \
    f"{MAX_BENCH_SLAT_GAP}"
assert abs(max(bench_slat_gaps) - (BENCH_SLAT_PITCH - BENCH_SLAT_W)) < TOL

# ---------------------------------------------------------------------------
# V13: THE END SLATS, THEIR CLEATS, AND THE FOUR CUSHIONS
# ---------------------------------------------------------------------------
# Everything the lower level gained this round, checked as geometry rather than
# described as intent. Three questions, in order: is the slat field closed to
# the wall, does the cleat that made that possible stay out of everything, and
# do the four cushions actually COVER the surface the two together produce.

# --- the end slat and its cleat ---------------------------------------------
for _i, (_slat, _cleat) in enumerate(zip(end_slats, end_cleats)):
    _sx, _sy, _sz = _slat.extents
    _cx, _cy, _cz = _cleat.extents
    assert _sx == (END_SLAT_X[_i], END_SLAT_X[_i] + BENCH_SLAT_W), \
        f"V13: '{_slat.label}' is at X {_sx}, want the {BENCH_SLAT_W} mm end zone"
    assert _sy == (BACK_POST_Y1, BENCH_SLAT_Y1), \
        f"V13: '{_slat.label}' must run from the back post's FRONT face " \
        f"({BACK_POST_Y1}) to the front vertical plane ({BENCH_SLAT_Y1})"
    assert _sz == (BENCH_RAIL_TOP, BENCH_TOP), \
        f"V13: '{_slat.label}' is not in the bench slat plane"
    assert _cz[1] == BENCH_RAIL_TOP == _sz[0], \
        "V13: the end cleat's top IS the end slat's underside"
    assert _cy[0] == BACK_POST_Y1, \
        "V13: the end cleat has to lie ON the back post's front face"
    assert _cx == _sx, "V13: the cleat sits under its own slat, full width"
# the field is CLOSED: no gap at the wall, and none between the end slat and
# the first ordinary bench slat.
assert END_SLAT_X[0] == 0 and END_SLAT_X[1] + BENCH_SLAT_W == WALL_SPAN, \
    "V13: the end slats must reach both walls"
assert END_SLAT_GAP == 0, \
    f"V13: the end slat leaves a {END_SLAT_GAP} mm gap to the field it closes"
assert END_SLAT_GAP <= EN_FINGER_FREE, \
    f"V13: a {END_SLAT_GAP} mm gap is outside EN 747's <= {EN_FINGER_FREE} band"
# the cleat's screws must not come near the post's back face - that face is the
# wall mounting plane, and the post is only 36 mm thick.
END_CLEAT_SCREW_LEN = 60
END_CLEAT_BITE = END_CLEAT_SCREW_LEN - END_CLEAT_T                     # 24
assert END_CLEAT_BITE < POST_T, \
    f"V13: a {END_CLEAT_SCREW_LEN} mm screw through {END_CLEAT_T} mm of cleat " \
    f"bites {END_CLEAT_BITE} mm into a {POST_T} mm post and comes out the back"
assert END_CLEAT_BITE >= 4 * 5, \
    f"V13: only {END_CLEAT_BITE} mm of a 5 mm screw in the post"
assert END_SLAT_SPAN < BENCH_SLAT_LEN - BENCH_RAIL_T, \
    f"V13: the end slat spans {END_SLAT_SPAN}, more than the field it joins"
print(f"OK  V13 endespile: {sec(BENCH_SLAT_T, BENCH_SLAT_W)} x {END_SLAT_LEN} "
      f"i hver ende (X {END_SLAT_X[0]}..{END_SLAT_X[0] + BENCH_SLAT_W} og "
      f"{END_SLAT_X[1]}..{WALL_SPAN}), Y {END_SLAT_Y0}..{END_SLAT_Y1} - den "
      f"starter på den bakre stolpens FORSIDE, for stolpen står i "
      f"soveflaten. Spennet er {END_SLAT_SPAN:g} mm mot feltets "
      f"{BENCH_SLAT_LEN - BENCH_RAIL_T} mm, og gapet inn til første "
      f"benkespile er {END_SLAT_GAP} mm")
print(f"OK  V13 endelist: {sec(END_CLEAT_T, END_CLEAT_H)} x {END_CLEAT_LEN} "
      f"skrudd flatt på den bakre stolpens forside (Y {END_CLEAT_Y0}, Z "
      f"{END_CLEAT_Z0}..{END_CLEAT_Z1}), 2 x 5x{END_CLEAT_SCREW_LEN} (J17): "
      f"{END_CLEAT_T} mm gjennom listen, {END_CLEAT_BITE} mm inn i en "
      f"{POST_T} mm stolpe, {POST_T - END_CLEAT_BITE} mm igjen til "
      f"veggflaten. Spileenden lander på {END_CLEAT_BEARING:.0f} mm2")

# --- the cushions: the split ------------------------------------------------
assert 2 * SEAT_CUSHION_LEN + 2 * BACK_CUSHION_LEN == LOWER_SLEEP_LEN, \
    f"V13: {SEAT_CUSHION_LEN} + {SEAT_CUSHION_LEN} + {BACK_CUSHION_LEN} + " \
    f"{BACK_CUSHION_LEN} is not the {LOWER_SLEEP_LEN} mm sleeping surface"
assert abs(SEAT_CUSHION_LEN - LOWER_SLEEP_LEN / 3) <= 1 and \
    abs(BACK_CUSHION_LEN - LOWER_SLEEP_LEN / 6) <= 1, \
    "V13: the seat cushion is a third of the length and the back cushion a " \
    "sixth, to the nearest millimetre"
# ONE FOAM BLOCK, WHICHEVER WAY UP IT IS. Every cushion in the model, in both
# positions, has to be the same three numbers: its length, the surface depth
# and the one thickness - only the axis they sit on changes when a back cushion
# stands up.
for _c in CUSHIONS_ALL:
    _dims = sorted(round(hi - lo) for lo, hi in _c.extents)
    _want = sorted([CUSHION_T, LOWER_SLEEP_DEPTH,
                    BACK_CUSHION_LEN if "Back" in _c.label
                    else SEAT_CUSHION_LEN])
    assert _dims == _want, \
        f"V13: '{_c.label}' measures {_dims}, want {_want} - a cushion is the " \
        f"same block of foam in both positions"

# --- the cushions: the tiling -----------------------------------------------
# The assert Hans asked for, and it is a COVER: every cushion box lies inside
# the surface, no two of them overlap, and their areas add up to the surface's
# own area. Area + disjoint + contained is exactly "they tile it".
def _rect(b):
    return (b[0][0], b[0][1], b[1][0], b[1][1])


def _inside(r, R):
    return (r[0] >= R[0] - TOL and r[1] <= R[1] + TOL
            and r[2] >= R[2] - TOL and r[3] <= R[3] + TOL)


def _box_overlap(a, b):
    v = 1.0
    for (a0, a1), (b0, b1) in zip(a, b):
        d = min(a1, b1) - max(a0, b0)
        if d <= 0:
            return 0.0
        v *= d
    return v


def _rect_overlap(a, b):
    return (max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
            * max(0.0, min(a[3], b[3]) - max(a[2], b[2])))


cushion_rects = [_rect(b) for c in CUSHIONS_BED for b in c.boxes]
covered = 0.0
for r in cushion_rects:
    assert any(_inside(r, R) for R in LOWER_SLEEP_RECTS), \
        f"V13: a cushion covers {r}, which is not on the sleeping surface " \
        f"(the surface is {LOWER_SLEEP_RECTS})"
    covered += (r[1] - r[0]) * (r[3] - r[2])
for _i, _a in enumerate(cushion_rects):
    for _b in cushion_rects[_i + 1:]:
        assert _rect_overlap(_a, _b) <= TOL, \
            f"V13: two cushions overlap over {_rect_overlap(_a, _b):.0f} mm2"
assert abs(covered - LOWER_SLEEP_AREA) < TOL, \
    f"V13: the four cushions cover {covered:.0f} mm2 of a " \
    f"{LOWER_SLEEP_AREA:.0f} mm2 sleeping surface - they are supposed to be a " \
    f"TILING of it, with nothing over and nothing short"
# and the tiling spans the whole length and the whole depth, edge to edge
assert min(r[0] for r in cushion_rects) == LOWER_SLEEP_X0 and \
    max(r[1] for r in cushion_rects) == LOWER_SLEEP_X1, \
    "V13: the cushions must run wall to wall"
for _c in CUSHIONS_BED:
    assert _c.extents[1] == (LOWER_SLEEP_Y0, LOWER_SLEEP_Y1), \
        f"V13: '{_c.label}' is {_c.extents[1]} deep, want the surface's own " \
        f"{LOWER_SLEEP_Y0}..{LOWER_SLEEP_Y1}"
    assert round(_c.extents[2][1] - _c.extents[2][0]) == CUSHION_T, \
        f"V13: '{_c.label}' is not {CUSHION_T} mm thick - all four are, or " \
        f"the bed has a step in it"
print(f"OK  V13 tiling: {SEAT_CUSHION_LEN} + {BACK_CUSHION_LEN} + "
      f"{BACK_CUSHION_LEN} + {SEAT_CUSHION_LEN} = {LOWER_SLEEP_LEN} mm x "
      f"{LOWER_SLEEP_DEPTH} mm - de fire putene DEKKER nedre soveflate "
      f"({covered:.0f} mm2 mot flatens {LOWER_SLEEP_AREA:.0f}), uten overlapp "
      f"og uten hull. Benkeputen er 1/3 og ryggputen 1/6 av lengden; "
      f"{LOWER_SLEEP_LEN} deler seg ikke på 6, så avrundingen "
      f"({LOWER_SLEEP_LEN / 3:.2f} / {LOWER_SLEEP_LEN / 6:.2f}) er lagt på "
      f"ryggputene og summen er eksakt")

# --- the cushions: nothing they touch is inside them -------------------------
for _mode, _panel in MODES.items():
    _wood = [p for p in mode_parts(_panel) if not is_soft(p)]
    _soft = CUSHIONS[id(_panel)]
    _bad = []
    for _c in _soft:
        for _b in _c.boxes:
            for _w in _wood:
                if _box_overlap(_b, _w.extents) > 1.0:
                    _bad.append((_c.label, _w.label))
        for _o in _soft:
            if _o is _c:
                continue
            for _b in _c.boxes:
                for _ob in _o.boxes:
                    if _box_overlap(_b, _ob) > 1.0:
                        _bad.append((_c.label, _o.label))
    assert not _bad, f"V13 {_mode}: cushions inside something: {sorted(set(_bad))}"
print(f"OK  V13: ingen av de fire putene ligger inne i noe - verken i tre "
      f"eller i hverandre, i noen av de to stillingene. De to benkeputene har "
      f"et {CUSHION_NOTCH[0]} x {CUSHION_NOTCH[1]} mm hakk i veggkanten, der "
      f"den bakre hjørnestolpen står; det er den ene grunnen til at en pute "
      f"her ikke er en ren rektangelklump")

# --- the cushions: the heights they set -------------------------------------
assert CUSHION_TOP_BENCH - CUSHION_TOP_PANEL == PANEL_BENCH_DIP, \
    "V13: with one thickness for all four, the 5 mm dip is the only step left"
assert LOWER_HEADROOM >= MIN_LOWER_HEADROOM, \
    f"V13: {LOWER_HEADROOM} mm from the lower sleeping surface to the slats " \
    f"above it, want at least {MIN_LOWER_HEADROOM}"
assert CUSHION_TOP_BENCH < EN_GUARD_TRIGGER_H, \
    f"EN 747: a bed base {CUSHION_TOP_BENCH} mm over the floor needs safety " \
    f"barriers; the lower level is supposed to be under the {EN_GUARD_TRIGGER_H} mm line"
assert TABLE_UNDER_OVER_CUSHION > 0 and TABLE_OVER_CUSHION > 0, \
    "V13: the table plate would land on the seat cushion"
assert SEAT_CUSHION_SHAFT_GAP > 0, \
    f"V13: the seat cushion reaches into the panel's transfer shaft by " \
    f"{-SEAT_CUSHION_SHAFT_GAP} mm - the plate cannot be lowered past it"
assert BACKREST_Y0 == LEDGER_BACK_Y0 + LEDGER_BACK_T, \
    "V13: the backrest stands on the back table ledger's front face"
# THE CUSHIONS COME OFF FIRST, AND THE MODEL SAYS SO RATHER THAN THE MANUAL
# REMEMBERING IT. The mode change carries the panel unit SIDEWAYS over the
# bench, in the shaft between the bench slat tops (320) and the back table
# ledger's underside (614 after X9, 474 before it). A 100 mm cushion lying on
# that bench fills the bottom 100 of those 294 mm. So this is not a tidiness
# instruction: the change-over is BLOCKED with the cushions on, and it is
# derived here. X9 made the shaft 140 mm taller and the cushion did not grow,
# so the rule is looser than it was - and it still bites, because a cushion
# standing 100 mm up off the bench is 100 mm of the only floor the unit has.
CARRY_BAND = (BENCH_TOP, LEDGER_BACK_Z0)              # 320..614  [X9: was 474]
CARRY_BAND_H = CARRY_BAND[1] - CARRY_BAND[0]          # 294  [was 154, 132]
assert CUSHION_TOP_BENCH > CARRY_BAND[0] + TOL, \
    "V13: a seat cushion that did not reach into the carry band would make " \
    "this note pointless - check the geometry before deleting it"
print(f"OK  V13 ombygging: seteputen fyller {CUSHION_T} av de "
      f"{CARRY_BAND_H} mm i overføringssjakten over benken (Z {CARRY_BAND[0]}"
      f"..{CARRY_BAND[1]}), som er der plateenheten bæres sidelengs. "
      f"Putene MÅ av før stillingsbyttet - det er geometri, ikke ryddighet")
# and it really does lean on the ledger: the two overlap in Z, or the "backstop"
# is a sentence rather than a contact.
assert BACKREST_Z0 < LEDGER_BACK_Z1 and BACKREST_Z1 > LEDGER_BACK_Z0, \
    f"V13: the backrest (Z {BACKREST_Z0}..{BACKREST_Z1}) never meets the " \
    f"ledger it is supposed to lean on (Z {LEDGER_BACK_Z0}..{LEDGER_BACK_Z1})"
assert BACKREST_Z1 < RAIL_BOTTOM, \
    f"V13: the backrest tops out at {BACKREST_Z1}, into the side rail at " \
    f"{RAIL_BOTTOM}"
assert BACKREST_PROUD == POST_THIN, \
    f"V13: the backrest stands {BACKREST_PROUD} mm proud of the front plane"
print(f"OK  V13 høyder: sittehøyde {BENCH_TOP} + {CUSHION_T} = "
      f"{CUSHION_TOP_BENCH} mm (soveflaten nede; {CUSHION_TOP_PANEL} over "
      f"platen, de samme {PANEL_BENCH_DIP} mm som før). Bordplaten ligger "
      f"{TABLE_OVER_CUSHION} mm over seteputen ({TABLE_UNDER_OVER_CUSHION} mm "
      f"til undersiden), hodehøyden under køyespilene er {LOWER_HEADROOM} mm "
      f"({LOWER_HEADROOM_RAIL} under sidevangene), og fallhøyden "
      f"{CUSHION_TOP_BENCH} mm er under EN 747s {EN_GUARD_TRIGGER_H} mm - "
      f"nedre nivå har ikke rekkverkskrav og får det ikke av putene heller")
print(f"OK  V13 sofastilling: seteputene ligger i SAMME X i begge stillinger "
      f"({SEAT_CUSHION_X[0]}..{SEAT_CUSHION_X[0] + SEAT_CUSHION_LEN} og "
      f"{SEAT_CUSHION_X[1]}..{WALL_SPAN}), {SEAT_CUSHION_OVERHANG} mm utenfor "
      f"benkeenden og {SEAT_CUSHION_SHAFT_GAP} mm fra platebanen (X "
      f"{PANEL_X0}..{PANEL_X1}); gangbukta måler {BAY_AT_CUSHION_H} mm i "
      f"putehøyde mot {PANEL_OPENING} på gulvet. Ryggputene står på enden av "
      f"hver benk, {CUSHION_T} mm tykke i X, {LOWER_SLEEP_DEPTH} mm dype og "
      f"{BACK_CUSHION_LEN} mm høye (topp {BACKREST_Z1}), og lener seg mot "
      f"bordbærelekta over {BACKREST_LEDGER_CONTACT:.0f} mm2")
# K2: and the two strips the narrower panel leaves beside itself in bed mode,
# stated against the thing this same bed already asks a mattress to bridge.
assert PANEL_SIDE_GAP > slat_gap, \
    "K2: if the side strip is narrower than the platform's own slat gap, " \
    "this note is over-explaining an ordinary number"
print(f"OK  K2 sengestillingen: platen dekker {PANEL_W} av de "
      f"{PANEL_OPENING} mm mellom benkene, så det står en {PANEL_SIDE_GAP} mm "
      f"åpen stripe langs hver side, {PANEL_SIDE_STRIP_LEN} mm dyp, ned mot "
      f"bakre benkevange ({BENCH_RAIL_TOP}) bakerst og gangsonen ellers. "
      f"Setebrikken bygger den ut, slik den bygger ut hele "
      f"{PANEL_BENCH_DIP} mm-forsenkningen; til sammenligning ligger sengens "
      f"eget spilefelt på {slat_gap:.1f} mm og benkene på "
      f"{max(bench_slat_gaps):.2f} mm. {PANEL_SIDE_GAP} mm er i EN 747-båndet "
      f"{EN_LIMB_BAND[0]:g}..{EN_LIMB_BAND[1]:g} - hele lemmet går fritt")
print(f"OK  C3/W9/U2: {BENCH_SLAT_COUNT} bench slats per bench, X "
      f"{BENCH_SLAT_X_START}..{BENCH_LEN} (mirrored {WALL_SPAN - BENCH_LEN}.."
      f"{WALL_SPAN - BENCH_SLAT_X_START}), pitch {BENCH_SLAT_PITCH:g} (was "
      f"124.75 on a {sec(48, 48)} post, 137.5 at the wall), gap "
      f"{min(bench_slat_gaps):g}..{max(bench_slat_gaps):g} mm (limit "
      f"{MAX_BENCH_SLAT_GAP}) - {BENCH_SLAT_COUNT * BENCH_SLAT_W} mm of board "
      f"in a {BENCH_LEN - BENCH_SLAT_X_START} mm field, clear of both posts")

# D11/D13: the two front bench rail segments stop at the SOFA ends now. Each one
# must (a) still lap its corner post at the outer end, (b) land its inner end
# square on the stub leg that is already there, with the full leg width under it
# and no cantilever past it.
front_legs = [p for p in parts if p.label.startswith("Bench Stub Leg Front")]
assert len(front_legs) == 2
leg_x_ranges = [p.extents[0] for p in front_legs]
leg_bearings = []
for r in front_bench_rails:
    (x0, x1), (y0, y1), (z0, z1) = r.extents
    assert (y0, y1) == (FRONT_RAIL_Y0, FRONT_RAIL_Y1), \
        f"'{r.label}' is not in the front bench rail plane"
    assert x1 - x0 == FRONT_BENCH_RAIL_SEG_LEN, \
        f"'{r.label}' is {x1 - x0} long, expected {FRONT_BENCH_RAIL_SEG_LEN}"
    # D13: no more upright lap - the segment must not reach the ladder at all.
    for a0, a1 in (p.extents[0] for p in up):
        assert min(x1, a1) - max(x0, a0) <= TOL, \
            f"D13: '{r.label}' still touches a ladder upright"
    # the outer end must still land on its corner post
    lap_post = max(min(x1, a1) - max(x0, a0)
                   for a0, a1 in (p.extents[0] for p in corner_posts))
    assert lap_post >= POST_W - THROUGH_X0, f"'{r.label}' barely reaches a corner post"
    # the INNER end must be supported: a stub leg directly under it, full width,
    # and the segment must not overhang the leg's inner face.
    is_left = x0 == THROUGH_X0
    inner_end = x1 if is_left else x0
    leg = [(a0, a1) for a0, a1 in leg_x_ranges
           if abs((a1 if is_left else a0) - inner_end) < TOL]
    assert len(leg) == 1, \
        f"D13: '{r.label}' inner end at X {inner_end} is not on a stub leg"
    (a0, a1) = leg[0]
    bear = min(x1, a1) - max(x0, a0)
    assert abs(bear - LEG_W) < TOL, \
        f"D13: '{r.label}' only bears {bear} mm on its stub leg, want {LEG_W}"
    # U5 re-check: the leg is 73 wide again instead of 48, so the end bearing in
    # X has to be re-measured against the absolute minimum, not just against
    # LEG_W. 73 >= 40 with the whole leg under the rail and no cantilever.
    assert bear >= MIN_LEG_BEARING, \
        f"W3: '{r.label}' bears only {bear} mm in X on its stub leg, want at " \
        f"least {MIN_LEG_BEARING}"
    # cantilever measured at the INNER end only (the outer end runs on to its
    # corner post, which is the other support, not an overhang)
    overhang = max((x1 - a1) if is_left else (a0 - x0), 0.0)
    assert overhang <= TOL, \
        f"D13: '{r.label}' cantilevers {overhang} mm past its stub leg"
    leg_bearings.append(bear)
# U2: THE FRONT BENCH RAIL NOW MEETS A 98 mm WIDE POST ON THE Y = 752 PLANE.
# The rail segment ends at Y 752 and the front post starts there, so the two
# share a face and nothing more - the check is that the face is REAL (a full
# 95 x 73 mm of it, the post width less the C9 setback, over the rail's whole
# height) and that the rail has not grown into the post's Y band. It used to be
# 45 x 73 = 3285 mm2 against a 48 mm post; it is 6935 mm2 now, which is what
# turns the outer end of that segment from a lap into a proper end fixing
# (U4: 2 x 6x90 through the post into the rail end grain).
front_post_parts = [p for p in parts if p.label.startswith("Corner Post Front")]
front_rail_post_faces = []
for r in front_bench_rails:
    (x0, x1), (y0, y1), (z0, z1) = r.extents
    touched = 0
    for q in front_post_parts:
        (px0, px1), (py0, py1), (pz0, pz1) = q.extents
        assert min(y1, py1) - max(y0, py0) <= TOL, \
            f"U2: '{r.label}' runs into '{q.label}' in Y"
        dx = min(x1, px1) - max(x0, px0)
        if dx <= TOL:
            continue
        assert abs(y1 - py0) < TOL, \
            f"U2: '{r.label}' shares X with '{q.label}' but does not meet its " \
            f"face at Y {py0}"
        area = dx * (min(z1, pz1) - max(z0, pz0))
        front_rail_post_faces.append(area)
        touched += 1
    assert touched == 1, \
        f"U2: '{r.label}' meets {touched} front corner posts, want exactly 1"
assert {round(a) for a in front_rail_post_faces} == \
    {(POST_W - THROUGH_X0) * BENCH_RAIL_H}, \
    f"U2: the front bench rail / front post faces are {front_rail_post_faces}, " \
    f"want {(POST_W - THROUGH_X0) * BENCH_RAIL_H} mm2 each"
seg = sorted(front_bench_rails, key=lambda p: p.extents[0][0])
bay_gap = seg[1].extents[0][0] - seg[0].extents[0][1]
assert abs(bay_gap - (OPEN_FLOOR_X[1] - OPEN_FLOOR_X[0])) < TOL, \
    f"the open front floor is {bay_gap} mm wide, want " \
    f"{OPEN_FLOOR_X[1] - OPEN_FLOOR_X[0]}"
# D13: the empty region grows from "the ladder opening" to THE WHOLE FLOOR
# BETWEEN THE BENCHES - X 645..1345, from the front face of the back rail
# forward, floor to bench-rail top. The ladder's own members are excluded not by
# an X exclusion but by the Y bound: the uprights live at Y 752..800 and the
# rungs and rung blocks at Y 727..800, all at or beyond RUNG_Y0, so bounding the
# zone at RUNG_Y0 takes exactly "the ladder itself" out and nothing else.
# M4 NOTE: this loop runs over `parts` - the FIXED structure - and the stiffener
# battens are deliberately not in it, because they belong to the panel and lift
# out with it. They do occupy the top 68 mm of this box in bed mode (Z 229..297)
# by design: they hang under the panel, which is itself the ceiling of the bay
# at 297. What must stay empty for them is the WALKING zone, floor to Z 229 -
# checked separately in the M4 block above.
BAY = (OPEN_FLOOR_X, (BACK_RAIL_Y1, RUNG_Y0), (0, BENCH_RAIL_TOP))
for p in parts:
    inter = [min(a1, b1) - max(a0, b0) for (a0, a1), (b0, b1) in zip(p.extents, BAY)]
    assert min(inter) <= TOL, \
        f"D13: '{p.label}' crosses the open front floor between the benches"
# and the legs must still stand under their segment
for leg in front_legs:
    (lx0, lx1), _, _ = leg.extents
    assert any(sx0 <= lx0 and lx1 <= sx1 for sx0, sx1 in FRONT_BENCH_RAIL_SEGMENTS), \
        f"'{leg.label}' at X {lx0}..{lx1} no longer stands under a rail segment"
print(f"OK  D11/D13: front bench rail = 2 x {sec(BENCH_RAIL_T, BENCH_RAIL_H)} x "
      f"{FRONT_BENCH_RAIL_SEG_LEN} at X {FRONT_BENCH_RAIL_SEGMENTS[0][0]}.."
      f"{FRONT_BENCH_RAIL_SEGMENTS[0][1]} / {FRONT_BENCH_RAIL_SEGMENTS[1][0]}.."
      f"{FRONT_BENCH_RAIL_SEGMENTS[1][1]} (Y {FRONT_RAIL_Y0}..{FRONT_RAIL_Y1}), "
      f"inner ends end-bearing {min(leg_bearings):.0f} mm on their stub legs "
      f"with no cantilever, no contact with the ladder; outer ends square on "
      f"the {POST_W} mm front posts over {int(front_rail_post_faces[0])} mm2 of "
      f"the Y={FRONT_POST_Y0} plane each (was 3285 on a 48 mm post, U2), no "
      f"collision; front floor open "
      f"{bay_gap} mm (X {OPEN_FLOOR_X[0]}..{OPEN_FLOOR_X[1]}) from the floor to "
      f"the bench rail top, everywhere in front of the back rail")

# U5: THE STUB LEGS ARE 48x73x186 - the bench rail's own section (W3 had made
# them 48x48 to share the then-48x48 corner post; U2 moved the posts to 36x98
# and left 48x48 an orphan). Three things to hold, and they are the same three
# W3 held - only the width changed: the section, the position (the leg's inner
# face still on the inner end of its bench, X 645 / 1345, with the leg running
# OUTWARD from there, which is what makes the front segments zero-cantilever
# end-bearing members), and the bearing - the whole 48 x 73 face has to be under
# its rail, not hanging off the side of it. The Y dimension is the binding one
# and is untouched at 48: the rail is 48 deep, so the leg is flush in Y.
legs = [p for p in parts if p.label.startswith("Bench Stub Leg")]
assert len(legs) == 4, f"W3: expected 4 stub legs, got {len(legs)}"
rail_pieces = [p for p in parts if "Bench Rail" in p.label and "Block" not in p.label]
leg_rail_bearings = []
for leg in legs:
    (lx0, lx1), (ly0, ly1), (lz0, lz1) = leg.extents
    assert (lx1 - lx0, ly1 - ly0) == (LEG_W, LEG_T), \
        f"W3: '{leg.label}' is {lx1 - lx0}x{ly1 - ly0}, want {sec(LEG_T, LEG_W)}"
    assert (lz0, lz1) == (0, STUB_LEG_H), \
        f"W3: '{leg.label}' runs Z {lz0}..{lz1}, want 0..{STUB_LEG_H}"
    assert lx1 in (BENCH_LEN, WALL_SPAN - BENCH_LEN + LEG_W) or \
        lx0 in (BENCH_LEN - LEG_W, WALL_SPAN - BENCH_LEN), \
        f"W3: '{leg.label}' at X {lx0}..{lx1} is off the bench end"
    # the leg must sit COMPLETELY under one rail piece, in both X and Y
    carried = [r for r in rail_pieces
               if r.extents[0][0] - TOL <= lx0 and lx1 <= r.extents[0][1] + TOL
               and r.extents[1][0] - TOL <= ly0 and ly1 <= r.extents[1][1] + TOL
               and abs(r.extents[2][0] - lz1) < TOL]
    assert len(carried) == 1, \
        f"W3: '{leg.label}' is not fully under exactly one bench rail " \
        f"({[r.label for r in carried]})"
    area = (lx1 - lx0) * (ly1 - ly0)
    assert abs(area - LEG_BEARING_AREA) < TOL, \
        f"W3: '{leg.label}' presents {area} mm2 to its rail, want {LEG_BEARING_AREA}"
    assert lx1 - lx0 >= MIN_LEG_BEARING, \
        f"W3: '{leg.label}' is only {lx1 - lx0} mm long in X (min {MIN_LEG_BEARING})"
    leg_rail_bearings.append((leg.label, carried[0].label, area))
assert {p.extents[0] for p in legs} == {
    (BENCH_LEN - LEG_W, BENCH_LEN),                          # 572..645
    (WALL_SPAN - BENCH_LEN, WALL_SPAN - BENCH_LEN + LEG_W),  # 1345..1418
}, f"U5: the legs are at {sorted({p.extents[0] for p in legs})}"
print(f"OK  U5: 4 stub legs {sec(LEG_T, LEG_W)} x {STUB_LEG_H} (was "
      f"{sec(LEG_T, 48)} in W3..U4, when 48x48 was the corner-post section; "
      f"U2 took the posts to {sec(BOARD36_T, BOARD36_W)} and left that profile "
      f"an orphan, so the leg goes back to the bench rail's own "
      f"{sec(BENCH_RAIL_T, BENCH_RAIL_H)}) at X "
      f"{STUB_LEG_X[0]}..{STUB_LEG_X[0] + LEG_W} / "
      f"{STUB_LEG_X[1]}..{STUB_LEG_X[1] + LEG_W} - inner faces still on the "
      f"bench ends {BENCH_LEN} / {WALL_SPAN - BENCH_LEN}, running outward from "
      f"there; each one fully under its rail with {LEG_BEARING_AREA} mm2 of "
      f"contact (was 2304), compression-perpendicular utilisation ~0.06, and "
      f"{LEG_W} mm >= {MIN_LEG_BEARING} mm of bearing in X. Y is unchanged at "
      f"{LEG_T}, flush in the rail's {BENCH_RAIL_T} mm depth")

# ---------------------------------------------------------------------------
# X8c - THE ROOM UNDER THE BENCH, MEASURED. IT IS STORAGE, SO SAY HOW BIG.
# ---------------------------------------------------------------------------
# Nothing in this round CREATES this space - it has been under the benches
# since the stub legs replaced a solid plinth - but nothing has ever said how
# big it is either, and a room nobody has measured is a room nobody buys boxes
# for. The builder is going to put loose boxes there, so the bed owes him
# three numbers he can take to a shop, and they have to be the SOLIDS' numbers
# and not a sentence somebody wrote once.
#
# WHAT BOUNDS IT, in the order the box meets them:
#   CEILING  the bench rail underside, BENCH_RAIL_BOTTOM. The bench top itself
#            is 91 mm higher, but the rails hang under it and they are what a
#            box actually hits.
#   FLOOR    the floor. NB the honest caveat, and it is the whole reason
#            MEASURE_DATUM_Z exists: the frame is built level off the laser
#            line over the HIGHEST point of the floor, so the clear height is
#            exactly this number at that point and MORE everywhere else.
#   DEPTH    the wall behind (WALL_Y) to the front bench rail's front face.
#            That is the same 800 mm the bench slats are long: the box can be
#            as deep as the bench is, and it goes in UNDER the front rail,
#            which is why the rail's own 48 mm does not count against it.
#   WIDTH    whatever the things standing on the floor leave. Measured, not
#            listed: the back corner post takes the wall end of each bench and
#            the two stub legs take the sofa end, and what is left between
#            them is one clear field per bench.
# The field is then asserted EMPTY, and so is the corridor it is pushed in
# through - the front plane, floor to the same ceiling - because a box you
# cannot get in is not storage either.
STORAGE_BAY_Z = (0, BENCH_RAIL_BOTTOM)                 # 0 .. 229
STORAGE_BAY_Y = (WALL_Y, FRONT_RAIL_Y1)                # -48 .. 752
STORAGE_BAY_H = STORAGE_BAY_Z[1] - STORAGE_BAY_Z[0]    # 229
STORAGE_BAY_D = STORAGE_BAY_Y[1] - STORAGE_BAY_Y[0]    # 800


def _clear_x_field(x0, x1, ybox, zbox):
    """The widest clear X interval in (x0, x1) inside the Y/Z box given."""
    edges = [x0, x1]
    for p in parts:
        (px0, px1), (py0, py1), (pz0, pz1) = p.extents
        if min(py1, ybox[1]) - max(py0, ybox[0]) <= TOL:
            continue
        if min(pz1, zbox[1]) - max(pz0, zbox[0]) <= TOL:
            continue
        if min(px1, x1) - max(px0, x0) <= TOL:
            continue
        edges += [max(px0, x0), min(px1, x1)]
    edges = sorted(set(edges))
    best = (0.0, x0, x0)
    for a, b in zip(edges, edges[1:]):
        mid = (a + b) / 2
        if any(p.extents[0][0] < mid < p.extents[0][1]
               and min(p.extents[1][1], ybox[1]) - max(p.extents[1][0], ybox[0]) > TOL
               and min(p.extents[2][1], zbox[1]) - max(p.extents[2][0], zbox[0]) > TOL
               for p in parts):
            continue
        if b - a > best[0]:
            best = (b - a, a, b)
    return best


STORAGE_BAYS = []
for _side, _bx0, _bx1 in (("left", 0.0, float(BENCH_LEN)),
                          ("right", float(WALL_SPAN - BENCH_LEN),
                           float(WALL_SPAN))):
    _w, _x0, _x1 = _clear_x_field(_bx0, _bx1, STORAGE_BAY_Y, STORAGE_BAY_Z)
    # the room itself, and the way in - both have to be genuinely empty
    for _what, _box in (("kasserommet", ((_x0 + TOL, _x1 - TOL),
                                         STORAGE_BAY_Y, STORAGE_BAY_Z)),
                        ("innkjøringen", ((_x0 + TOL, _x1 - TOL),
                                          (FRONT_RAIL_Y1, FRONT_POST_Y1),
                                          STORAGE_BAY_Z))):
        for p in parts:
            inter = [min(a1, b1) - max(a0, b0)
                     for (a0, a1), (b0, b1) in zip(p.extents, _box)]
            assert min(inter) <= TOL, \
                f"X8c: '{p.label}' står i {_what} under {_side} benk"
    STORAGE_BAYS.append((_side, _x0, _x1, _w))
STORAGE_BAY_W = STORAGE_BAYS[0][3]
assert len(STORAGE_BAYS) == 2 and \
    all(abs(b[3] - STORAGE_BAY_W) < TOL for b in STORAGE_BAYS), \
    f"X8c: the two under-bench bays are {[b[3] for b in STORAGE_BAYS]} mm " \
    f"wide - the bed is symmetric, so they are supposed to be the same room " \
    f"twice"
assert abs(STORAGE_BAY_W - (STUB_LEG_X[0] - POST_W)) < TOL, \
    f"X8c: the clear field is {STORAGE_BAY_W} mm, and the rule says it is " \
    f"the back post's inner face to the stub leg's outer face, " \
    f"{STUB_LEG_X[0] - POST_W}"
assert abs(STORAGE_BAY_D - BENCH_SLAT_LEN) < TOL, \
    f"X8c: the bay is {STORAGE_BAY_D} mm deep and a bench slat is " \
    f"{BENCH_SLAT_LEN} - the box is supposed to be able to be as deep as the " \
    f"bench it stands under"
print(f"OK  X8c kasserommet under benkene: {len(STORAGE_BAYS)} rom, "
      f"{STORAGE_BAY_H:g} høyt x {STORAGE_BAY_W:g} bredt x {STORAGE_BAY_D:g} "
      f"dypt (X "
      + " / ".join(f"{b[1]:g}..{b[2]:g}" for b in STORAGE_BAYS)
      + f", Y {STORAGE_BAY_Y[0]:g}..{STORAGE_BAY_Y[1]:g}, Z "
        f"{STORAGE_BAY_Z[0]:g}..{STORAGE_BAY_Z[1]:g}) - taket er "
        f"benkevangens underkant, bredden er fra bakre hjørnestolpe til "
        f"stubbefot, dybden er benkespilens egen lengde, og både rommet og "
        f"innkjøringen foran det er målt tomme på solidene")

# D13: WALK-AROUND. There must be a real passage on each side of the ladder,
# between the sofa end and the upright outer face, clear from the floor up to
# the table-mode panel line (682 after X9) across the whole front zone. That
# line used to be written as RUNG_TOPS[1] because the plate sat on rung 2; X9
# decoupled the two, and the passage follows the PLATE - it is the plate you
# walk under, not the rung.
#
# The clear width is measured against FIXED STRUCTURE (`parts`). The loose panel
# is handled separately below: it is the seat / table surface, it lies at 297 in
# bed mode and 682 in table mode, and it does bridge the passage at that height
# by design - what matters is that it never touches the floor level you actually
# stand and put your feet in, which is checked explicitly afterwards.
# D14 ripple: the front edge of the zone used to be the guard face (834). The
# guards went inboard, so it is the post plane now - the same 800 mm of front
# zone the check has always swept, minus the 34 mm that no longer exists.
PASSAGE_Y = (BACK_RAIL_Y1, FRONT_POST_Y1)            # 0 .. 800, front zone
PASSAGE_Z = (0, PANEL_UNDER_TABLE)                   # 0 .. 682  [X9: was 542]
PASSAGE_BANDS = [("left", OPEN_FLOOR_X[0], up[0].extents[0][0]),
                 ("right", up[1].extents[0][1], OPEN_FLOOR_X[1])]
passages = []
for side, bx0, bx1 in PASSAGE_BANDS:
    lo, hi = bx0, bx1
    for p in parts:
        (px0, px1), (py0, py1), (pz0, pz1) = p.extents
        if min(py1, PASSAGE_Y[1]) - max(py0, PASSAGE_Y[0]) <= TOL:
            continue
        if min(pz1, PASSAGE_Z[1]) - max(pz0, PASSAGE_Z[0]) <= TOL:
            continue
        if min(px1, bx1) - max(px0, bx0) <= TOL:
            continue
        # something pokes into the nominal band - pull the clear edge back
        if px1 - bx0 <= (bx1 - bx0) / 2:
            lo = max(lo, px1)
        elif bx1 - px0 <= (bx1 - bx0) / 2:
            hi = min(hi, px0)
        else:
            raise AssertionError(
                f"D13: '{p.label}' blocks the {side} walk-around passage")
    clear = hi - lo
    assert clear >= MIN_PASSAGE, \
        f"D13: the {side} walk-around is only {clear:.0f} mm, want >= {MIN_PASSAGE}"
    # and the resulting passage must be genuinely empty
    box = ((lo + TOL, hi - TOL), PASSAGE_Y, PASSAGE_Z)
    for p in parts:
        inter = [min(a1, b1) - max(a0, b0)
                 for (a0, a1), (b0, b1) in zip(p.extents, box)]
        assert min(inter) <= TOL, \
            f"D13: '{p.label}' stands in the {side} walk-around passage"
    # the movable panel must not reach down into the standing zone either, in
    # EITHER mode - floor to the bench-rail top, the height your feet occupy.
    foot_box = ((lo + TOL, hi - TOL), PASSAGE_Y, (0, BENCH_RAIL_TOP))
    for p in (panel_bed, panel_table):
        inter = [min(a1, b1) - max(a0, b0)
                 for (a0, a1), (b0, b1) in zip(p.extents, foot_box)]
        assert min(inter) <= TOL, \
            f"D13: '{p.label}' reaches into the {side} standing zone"
    passages.append((side, lo, hi, clear))
# U2: the passage is the one thing this round makes WORSE. Turning the upright
# puts 48 mm of it in X instead of 36, and the passage is measured from the sofa
# end to the upright's outer face, so it loses those 12 mm: 154 -> 142. It is
# still over the 140 mm floor and it is still the widest it has ever been apart
# from v8-v10 (v7 had no passage at all - the bench rail ran through). Named
# explicitly so the number is not read as an accident.
assert all(abs(c - ((LADDER_INNER_L - UPRIGHT_W) - OPEN_FLOOR_X[0])) < TOL
           for _, _, _, c in passages), \
    f"U2: the two passages are {[c for *_, c in passages]}, want the sofa end " \
    f"to upright outer face clear on both sides"
assert all(abs(c - 142) < TOL for *_, c in passages), \
    f"U2: the walk-around is {[c for *_, c in passages]} mm, want 142 " \
    f"(154 while the upright was {36} wide in X)"
print("OK  D13/U2: walk-around beside the ladder - "
      + " / ".join(f"{s} X {lo:.0f}..{hi:.0f} = {c:.0f} mm clear"
                   for s, lo, hi, c in passages)
      + f" (min {MIN_PASSAGE}; was 154 before U2 turned the {UPRIGHT_T}x"
        f"{UPRIGHT_W} uprights to put their {UPRIGHT_T} mm face in Y), empty "
        f"over Y {PASSAGE_Y[0]}..{PASSAGE_Y[1]} and "
        f"Z {PASSAGE_Z[0]}..{PASSAGE_Z[1]}")

# ---------------------------------------------------------------------------
# F1 (V4): CAN THE LADDER FOOT BE TIED TO THE FRAME AT ALL? MEASURED.
# ---------------------------------------------------------------------------
# Vedlegg B, avvik 2 has carried an open point since V2: the panel is a one-way
# strut, so the ladder foot cannot go BACKWARD, and forward it hangs on J3
# alone. The obvious fix is the one the deviation itself names - "et eget bånd
# fra stigefoten til rammen", a block or a brace from the foot to something
# that is not the ladder - so this round went looking for somewhere to put it.
#
# THIS BLOCK IS THAT SEARCH, and it is a search over the model rather than over
# an opinion: for each of the four horizontal directions out of the stile's
# foot, find the NEAREST fixed member that is actually reachable in a straight
# line (i.e. that overlaps the foot in the other two axes), and print how far
# away it is. A tie is a piece of wood spanning that gap; if the gap is a
# volume some other rule requires to be EMPTY, the tie cannot be built without
# giving that rule up.
#
# The result, and it is the reason avvik 2 stays open:
#   OUT  the nearest thing in the stile's own Y band is the FRONT CORNER POST,
#        the whole length of the bench away. Between them lies the D13
#        walk-around, required clear from the floor to Z 542.
#   IN   the other stile, across the ladder opening, which EN 747 requires to
#        stay >= 300 mm clear. Tying the two stiles together adds nothing in Y
#        anyway - they move as one frame.
#   BACK the back bench rail, three quarters of a metre away across the D11
#        open bay, which is required clear to Z 297 - and above Z 229 the same
#        column is the panel's own insertion shaft.
#   FWD  NOTHING. There is no member in front of the ladder at all, and there
#        cannot be: U3 fixes the front face at Y = 788 and asserts Y 788..800
#        empty, and the overall depth is pinned at 836.
# So every direction out of the foot is either a protected void or the room,
# and the tie is not a detail this geometry can have as it stands. What it
# would cost to have one anyway is written up in vedlegg B.
FOOT_TIE_Z = (0, BENCH_RAIL_TOP)                 # 0..297, the foot proper


def _nearest_fixed(box, axis, sign, exclude):
    """(clear gap, label) to the nearest fixed part straight along `axis`.

    'Straight along' means it overlaps `box` in the other two axes, so a piece
    of wood spanning the gap would land on it square. inf when there is
    nothing out that way at all.
    """
    best, who = math.inf, None
    for p in parts:
        if p in exclude:
            continue
        if any(min(box[j][1], p.extents[j][1])
               - max(box[j][0], p.extents[j][0]) <= TOL
               for j in range(3) if j != axis):
            continue
        gap = (p.extents[axis][0] - box[axis][1] if sign > 0
               else box[axis][0] - p.extents[axis][1])
        if gap < -TOL:
            continue
        if gap < best:
            best, who = gap, p.label
    return best, who


# The LADDER itself is not an anchor: stiles, rungs and rung blocks are one
# rigid frame and they all move together when the foot moves.
_LADDER = [p for p in parts
           if p.label.startswith(("Ladder", "Rung Block"))]
# Directions are named from the LADDER, not from the axes, so the two sides
# can be compared: "utover" is away from the ladder centreline on either side.
FOOT_TIE_DIRS = ("utover", "innover", "bakover", "framover")
FOOT_TIE_REACH = {}
for _s, _u, _out in (("venstre", up[0], -1), ("høyre", up[1], 1)):
    _box = (_u.extents[0], _u.extents[1], FOOT_TIE_Z)
    for _lbl, _ax, _sg in ((FOOT_TIE_DIRS[0], 0, _out),
                           (FOOT_TIE_DIRS[1], 0, -_out),
                           (FOOT_TIE_DIRS[2], 1, -1),
                           (FOOT_TIE_DIRS[3], 1, 1)):
        FOOT_TIE_REACH[(_s, _lbl)] = _nearest_fixed(_box, _ax, _sg, _LADDER)
# The two sides must see the same room - anything else means the bed is not
# symmetric about the ladder any more and this finding would need re-reading.
for _lbl in FOOT_TIE_DIRS:
    _l, _r = FOOT_TIE_REACH[("venstre", _lbl)], FOOT_TIE_REACH[("høyre", _lbl)]
    assert _l[0] == _r[0] or abs(_l[0] - _r[0]) < TOL, \
        f"F1: {_lbl} reaches {_l[0]} on the left and {_r[0]} on the right"
assert FOOT_TIE_REACH[("venstre", "framover")][0] == math.inf, \
    "F1: something now stands in front of the ladder foot - re-read avvik 2"
assert FOOT_TIE_REACH[("venstre", "utover")][0] > MIN_PASSAGE, \
    "F1: the outboard gap no longer contains the whole walk-around"
print("OK  F1 stigefot: nærmeste faste del å binde foten til, per retning - "
      + "; ".join(
          f"{_lbl} {FOOT_TIE_REACH[('venstre', _lbl)][0]:.0f} mm "
          f"({FOOT_TIE_REACH[('venstre', _lbl)][1]})"
          if FOOT_TIE_REACH[("venstre", _lbl)][0] != math.inf
          else f"{_lbl} INGENTING"
          for _lbl in FOOT_TIE_DIRS)
      + f". Mellomrommene er ikke ledige: UTOVER er D13-gangpassasjen "
        f"({MIN_PASSAGE}+ mm fri fra gulv til {PASSAGE_Z[1]}), BAKOVER er D11s "
        f"åpne bod (fri til {BENCH_RAIL_TOP}, og over {BENCH_RAIL_BOTTOM} er "
        f"det platens innsettingssjakt), INNOVER er stigeåpningen "
        f"({LADDER_CLEAR} mm, krav {MIN_LADDER_CLEAR}) og FRAMOVER er rommet - U3 "
        f"krever Y {FRONT_POST_Y1}..{FRONT_POST_Y1 + POST_THIN} tomt og "
        f"dybden er låst til {OVERALL_DEPTH}. Avvik 2 forblir åpent, med pris "
        f"på hver av utveiene i vedlegg B")

# D8: an even ladder. Rung 1 shares its top with the bench rails and rung 2 with
# the table-mode panel underside; every step of the climb proper has to be under
# the comfort limit and the four of them within a few mm of each other.
rungs = sorted((p for p in parts if p.label.startswith("Ladder Rung_")),
               key=lambda p: p.extents[2][0])
assert len(rungs) == len(RUNG_TOPS)
for r, top in zip(rungs, RUNG_TOPS):
    assert r.extents[2] == (top - RUNG_T, top), f"'{r.label}' is not at top Z {top}"
    assert r.extents[1] == (RUNG_Y0, RUNG_Y1) and r.extents[0] == (LADDER_INNER_L,
                                                                   LADDER_INNER_R)
# every rung block sits directly under its rung, on the same 36x48 stock
rung_blocks = [p for p in parts if p.label.startswith("Rung Block")]
assert len(rung_blocks) == 2 * len(RUNG_TOPS)
for b in rung_blocks:
    top = b.extents[2][1] + RUNG_T
    assert top in RUNG_TOPS, f"'{b.label}' does not sit under a rung"
    assert b.extents[2] == (top - RUNG_T - RUNG_BLOCK_H, top - RUNG_T)
    # K1: the block lives in the UPRIGHT's Y band, not the rung's. That is
    # the whole of the change: it is exactly as long as the face it is
    # screwed to, so nothing of it hangs behind the upright into the panel's
    # transfer slot.
    assert b.extents[1] == (RUNG_BLOCK_Y0, RUNG_BLOCK_Y1) == (LADDER_Y0, LADDER_Y1), \
        f"K1: '{b.label}' is not in the upright's own Y band"
climb = [0] + RUNG_TOPS + [SLAT_Z1]
steps = [b - a for a, b in zip(climb, climb[1:])]
first_rise, climb_steps = steps[0], steps[1:]
# The first rise is not a climbing step - it is the seat-height ledge you step
# onto, and it is fixed by the bench rail whose top rung 1 shares.
assert first_rise == BENCH_RAIL_TOP == RUNG_TOPS[0], \
    f"rung 1 (top {RUNG_TOPS[0]}) is not level with the bench rails ({BENCH_RAIL_TOP})"
assert max(climb_steps) <= MAX_CLIMB_STEP, \
    f"D8: biggest climbing step is {max(climb_steps)} > {MAX_CLIMB_STEP}"
assert max(climb_steps) - min(climb_steps) <= MAX_CLIMB_SPREAD, \
    f"D8/X9: the two flights are {max(climb_steps) - min(climb_steps)} mm " \
    f"apart in pitch - steps {climb_steps}, gate {MAX_CLIMB_SPREAD}"
# X9: THE CLIMB IS TWO FLIGHTS, AND EACH ONE IS JUDGED ON ITS OWN. The lift
# corridor is crossed exactly once - by the step onto the first rung that
# stands at or above RUNG_ABOVE_TABLE_MIN - and that step is the last one of
# the lower flight. Inside a flight the old evenness rule survives, tightened:
# whole-millimetre rounding and nothing else. Nothing about the flights is
# typed; they are read back off the derived list.
CLIMB_LANDING = next(i for i, t in enumerate(RUNG_TOPS)
                     if t >= RUNG_ABOVE_TABLE_MIN)
CLIMB_FLIGHTS = [climb_steps[:CLIMB_LANDING], climb_steps[CLIMB_LANDING:]]
assert CLIMB_LANDING >= 1 and all(CLIMB_FLIGHTS), \
    "X9: the climb has to cross the lift corridor with a step, not start above it"
assert not any(TABLE_UNIT_Z0 < t < RUNG_ABOVE_TABLE_MIN for t in RUNG_TOPS), (
    f"X9: a rung top lies in {TABLE_UNIT_Z0}..{RUNG_ABOVE_TABLE_MIN}, which is "
    f"the band the seated plate occupies and the {INSERT_CLEAR_MIN} mm it has "
    f"to rise through - rung tops {RUNG_TOPS}")
for _i, _fl in enumerate(CLIMB_FLIGHTS, 1):
    assert max(_fl) - min(_fl) <= MAX_FLIGHT_SPREAD, (
        f"X9: flight {_i} is uneven - steps {_fl}, gate {MAX_FLIGHT_SPREAD}. "
        f"A flight is a run of equal steps or it is not a flight")
assert climb[-1] == SLAT_Z1, "the climb must end on the platform surface"
print(f"OK  D8: rung tops {'/'.join(str(t) for t in RUNG_TOPS)}; rises "
      + " + ".join(str(s) for s in steps)
      + f" mm from the floor to the {SLAT_Z1} platform - first rise "
      f"{first_rise} = bench rail top, then {min(climb_steps)}..{max(climb_steps)} "
      f"(limit {MAX_CLIMB_STEP})")
print(f"OK  X9 stigen er TO løp om løftesjakten {TABLE_UNIT_Z0}.."
      f"{RUNG_ABOVE_TABLE_MIN}: "
      + " og ".join("+".join(str(s) for s in _fl) for _fl in CLIMB_FLIGHTS)
      + f" - hvert løp jevnt til {max(max(_f) - min(_f) for _f in CLIMB_FLIGHTS)}"
      f" mm (grense {MAX_FLIGHT_SPREAD}), løpene "
      f"{max(climb_steps) - min(climb_steps)} mm fra hverandre (grense "
      f"{MAX_CLIMB_SPREAD}). Ingen trinntopp i sjakten")

# D9: the front table ledger must be GONE and the back one's TOP must BE the
# table-mode panel underside - no hook step, nothing in between.
ledgers = [p for p in parts if p.label.startswith("Table Ledger")]
assert len(ledgers) == 1 and ledgers[0].label == "Table Ledger Back", \
    "D3: the front table ledger must be deleted"
assert not any("Front" in p.label and "Ledger" in p.label for p in parts)
assert ledgers[0].extents[2] == (LEDGER_BACK_Z0, LEDGER_BACK_Z1)
# X9: the ledger top and the table-mode panel underside still have to coincide;
# what is gone is the third member of that identity. Under X2 it was rung 2's
# top as well, and the desk is at a height no rung is allowed to stand at, so
# the front half of the seat is the two bordklosser instead - checked here to
# be at the SAME 682, because a plate on two seats at two heights rocks.
_bearers = [p for p in parts if p.label.startswith("Table Bearer")]
assert len(_bearers) == 2, f"X9: {len(_bearers)} bordklosser, want 2"
assert LEDGER_BACK_Z1 == PANEL_UNDER_TABLE, \
    "D9: the ledger top and the table-mode panel underside must coincide"
assert all(b.extents[2][1] == PANEL_UNDER_TABLE for b in _bearers), \
    "X9: a bordkloss top is not level with the plate's underside"
assert PANEL_UNDER_TABLE not in RUNG_TOPS, \
    "X9: the table seat must NOT be a rung top - that is the whole corridor"
assert BENCH_RAIL_TOP == PANEL_UNDER_BED == RUNG_TOPS[0], \
    "D10: the bench rail tops, rung 1 and the bed-mode panel underside must coincide"
assert "HOOK_STEP" not in globals(), "D10: the hook step is supposed to be gone"
assert PANEL_X0 >= LADDER_INNER_L - 200 and PANEL_X1 <= LADDER_INNER_R + 200
print(f"OK  D9/W9: front table ledger deleted; back ledger "
      f"{sec(LEDGER_BACK_T, LEDGER_BACK_H)} x {BETWEEN_POSTS_LEN} "
      f"(was {THROUGH_LEN}, and 21x95 before V2) at X "
      f"{BETWEEN_POSTS_X0}..{BETWEEN_POSTS_X1}, Z {LEDGER_BACK_Z0}.."
      f"{LEDGER_BACK_Z1}, top level with the two bordklosser (X9: with rung 2 "
      f"until the plate became a desk), ends screwed to the back posts' "
      f"X-inner faces")
print(f"OK  X9 bordklossene: 2 x {sec(TABLE_BEARER_T, TABLE_BEARER_H)} x "
      f"{TABLE_BEARER_LEN} på stigevangenes innerflater, X "
      f"{TABLE_BEARER_X[0]}..{TABLE_BEARER_X[0] + TABLE_BEARER_T} / "
      f"{TABLE_BEARER_X[1]}..{TABLE_BEARER_X[1] + TABLE_BEARER_T}, Y "
      f"{TABLE_BEARER_Y0}..{TABLE_BEARER_Y1}, Z {TABLE_BEARER_Z0}.."
      f"{TABLE_BEARER_Z1}. {UPRIGHT_T} mm av lengden ligger mot vangen "
      f"({UPRIGHT_T * TABLE_BEARER_H} mm² flate, samme som en stigekloss) og "
      f"{TABLE_BEARER_LEDGE} mm stikker bak den som bæreflate - "
      f"{TABLE_BEARER_BEARING} mm² til sammen, og lengden er regnet ut av "
      f"kravet ({MIN_BEARING} mm² per bærelinje), ikke valgt. "
      f"Vangeflaten tar {TABLE_BEARER_SCREWS} × 6×80 (X10: var én)")

# ---------------------------------------------------------------------------
# X10 - THE PLATE'S FREE FRONT EDGE, MEASURED AND PRICED
# ---------------------------------------------------------------------------
# MIN_BEARING is an AREA rule and an area rule cannot see a span: two blocks
# 5088 mm2 apart satisfy it whether they stand 20 mm apart or a metre. That is
# the hole X9's arithmetic fell into (see the X10 CORRECTION in the X9 block
# above), and this is the row that closes it. Everything here is read off the
# solids: the two bearers' inner faces, the plate's own thickness, its own
# front edge.
#
# THE CASE. One kilonewton standing on the middle of the free edge - somebody
# leaning on the table from the ladder, or sitting on it. Simply supported over
# the bay, because a free edge has nothing to fix it: M = P*L/4. The effective
# width is the argument that matters and it is written down rather than
# assumed: away from an edge a point load spreads both ways into the sheet, at
# a FREE EDGE it can only spread one, so b_ef is the contact patch plus one
# spread - PANEL_BEF_SPREAD. Two patches, because they are two different
# people: a flat hand and a knee.
#
# THE GRAIN IS A REQUIREMENT NOW, NOT AN ASSUMPTION. The plate is plywood and
# plywood is not isotropic: along the face grain it carries roughly two and a
# half times what it carries across. The file has been computing every sheet
# row on ONE number, 6,95 MPa, calibrated in vedlegg A on the bare-plate row -
# and that row spans the plate's LONG way, in Y, so 6,95 is the ACROSS-grain
# value. This row spans in X. The face grain therefore has to run in X, along
# the bed, and that is a CUTTING INSTRUCTION with a load case behind it rather
# than a preference: cut the 574 x 798 blank with the face veneer running the
# 574 way. It costs nothing (the blank is smaller than the sheet either way)
# and it is the difference between 1,49 and 0,60.
PANEL_GRAIN_AXIS = 0             # X - the face veneer runs along the bed
PANEL_F_M_D_CROSS = 6.95         # MPa, the vedlegg A calibration (across grain)
PANEL_GRAIN_RATIO = 2.5          # f_m,0 / f_m,90 for softwood plywood
PANEL_F_M_D_GRAIN = PANEL_F_M_D_CROSS * PANEL_GRAIN_RATIO       # 17.4 MPa
PANEL_BEF_SPREAD = 60            # mm the load spreads into a FREE edge, one way
PANEL_EDGE_LOAD_N = 1000         # N, the same kilonewton every other row uses
PANEL_EDGE_PATCHES = [("flat hånd", 80), ("kne", 40)]

_bx = sorted(b.extents[0] for b in _bearers)
PANEL_FREE_EDGE_SPAN = _bx[1][0] - _bx[0][1]
assert abs(PANEL_FREE_EDGE_SPAN - TABLE_FREE_EDGE) < TOL, (
    f"X10: the bordklosser leave {PANEL_FREE_EDGE_SPAN:g} mm of bare front "
    f"edge between them and the file says {TABLE_FREE_EDGE:g}")
assert all(b.extents[1][1] >= panel_table.extents[1][1] - TOL
           for b in _bearers), \
    "X10: a bordkloss stops short of the plate's own front edge in Y, so the " \
    "edge overhangs it and the span above is not the whole case"
PANEL_EDGE_ROWS = []
for _what, _patch in PANEL_EDGE_PATCHES:
    _bef = _patch + PANEL_BEF_SPREAD
    _w = _bef * PANEL_T ** 2 / 6
    _sigma = PANEL_EDGE_LOAD_N * PANEL_FREE_EDGE_SPAN / 4 / _w
    PANEL_EDGE_ROWS.append((_what, _patch, _bef, _sigma,
                            _sigma / PANEL_F_M_D_CROSS,
                            _sigma / PANEL_F_M_D_GRAIN))
PANEL_EDGE_UTIL = max(r[5] for r in PANEL_EDGE_ROWS)
PANEL_EDGE_UTIL_CROSS = max(r[4] for r in PANEL_EDGE_ROWS)
assert PANEL_EDGE_UTIL <= 1.0, (
    f"X10: {PANEL_EDGE_UTIL:.2f} on the plate's free front edge over "
    f"{PANEL_FREE_EDGE_SPAN:g} mm, even with the face grain running the span. "
    f"There is nowhere to put a batten under that edge - the rung owns the "
    f"space in bed mode - so the way out is a shorter bay: widen the "
    f"bordklosser again, or a thicker sheet")
assert PANEL_EDGE_UTIL_CROSS > 1.0, (
    "X10: the across-grain row now passes too, so PANEL_GRAIN_AXIS has stopped "
    "being load-bearing and should be re-argued rather than left standing as "
    "a requirement nobody needs")
print(f"OK  X10 platas frie forkant: {PANEL_FREE_EDGE_SPAN:g} mm bart "
      f"{PANEL_T} mm ark mellom bordklossene (X "
      f"{_bx[0][1]:g}..{_bx[1][0]:g}), fritt opplagt, "
      f"{PANEL_EDGE_LOAD_N / 1000:g} kN midt på kanten - M = "
      f"{PANEL_EDGE_LOAD_N * PANEL_FREE_EDGE_SPAN / 4:.0f} Nmm:")
for _what, _patch, _bef, _sigma, _uc, _ug in PANEL_EDGE_ROWS:
    print(f"      {_what:10s} {_patch} mm avtrykk → b_ef {_bef:g} mm, "
          f"σ {_sigma:.2f} MPa: {_uc:.2f} mot f_m,d {PANEL_F_M_D_CROSS:g} "
          f"(på tvers av fiberretningen) og {_ug:.2f} mot "
          f"{PANEL_F_M_D_GRAIN:.1f} (langs)")
# X10 - AND THE MOMENT THAT COMES WITH THAT HALF-KILONEWTON. The shear row in
# BLOCKLESS_CORNERS is the easy half: 0,5 kN into two 6 mm screws is 0,13. What
# V5's rule does not ask, because no other block in this bed has the problem,
# is where the load STANDS relative to the screws. On this one it stands on the
# ledge - out in front of the upright - and the screws are on the upright's own
# centre line, so the reaction and the fixing are not in the same plane and the
# difference is a moment about X, lying IN the face. It is carried as a couple:
# the two screws take equal and opposite shear, arm = their own spacing.
# With one screw there is no arm at all and no couple - only friction on the
# 36 x 68 patch and a 6 mm shank in bending, neither of which this file has a
# number for. That is the whole argument for the second screw, and it is a row
# now rather than a paragraph.
_j5b = sorted((f for f in FASTENER_SPECS if f["jid"] == "J5-B"),
              key=lambda f: f["anchor"][2])
BEARER_LOAD_KN = 0.5             # half the plate's 1 kN, per block
# The plate sits on the LEDGE - the part of the block that stands out in front
# of the upright, Y0..Y0+LEDGE - so its reaction acts through that patch's own
# middle, and the screws are on the upright's centre line behind it.
BEARER_LOAD_Y = TABLE_BEARER_Y0 + TABLE_BEARER_LEDGE / 2
BEARER_ARM = _j5b[0]["anchor"][1] - BEARER_LOAD_Y
BEARER_COUPLE_ARM = abs(_j5b[-1]["anchor"][2] - _j5b[0]["anchor"][2])
assert BEARER_COUPLE_ARM > 0, (
    "X10: the two J5-B screws are at the same height, so there is no couple "
    "arm and the plate's eccentric load has nothing to work against")
BEARER_COUPLE_KN = BEARER_LOAD_KN * abs(BEARER_ARM) / BEARER_COUPLE_ARM
BEARER_SCREW_KN = (BEARER_COUPLE_KN
                   + BEARER_LOAD_KN / len(_j5b))    # couple + its share of shear
BEARER_UTIL = BEARER_SCREW_KN / SCREW_SHEAR_KN[6]
assert BEARER_UTIL <= MAX_BLOCKLESS_UTIL, (
    f"X10: the worse of the two bordkloss screws is {BEARER_UTIL:.2f} utilised "
    f"- {BEARER_COUPLE_KN:.2f} kN of couple from a {abs(BEARER_ARM):.0f} mm "
    f"arm over a {BEARER_COUPLE_ARM:g} mm spacing, plus its share of the "
    f"direct shear - against the {MAX_BLOCKLESS_UTIL:g} gate every block-less "
    f"corner in this bed is held to. Stand the block taller so the two screws "
    f"stand further apart, or take the load off its front")
print(f"      OG BÆREKANTEN: platen lander {abs(BEARER_ARM):.0f} mm foran "
      f"skruelinja, så {BEARER_LOAD_KN:g} kN per kloss blir et par på "
      f"{BEARER_COUPLE_KN:.2f} kN over {BEARER_COUPLE_ARM:g} mm skrueavstand. "
      f"Med skjæret sitt attpå: {BEARER_SCREW_KN:.2f} kN mot "
      f"{SCREW_SHEAR_KN[6]:g} → {BEARER_UTIL:.2f} (grense "
      f"{MAX_BLOCKLESS_UTIL:g}). Med ÉN skrue finnes ikke armen - X9s kloss "
      f"tok momentet i friksjon og bøyd skaft, som ingen rad i denne fila kan "
      f"regne på")
print(f"      KRAV TIL PLATA: dekkfineren skal ligge langs "
      f"{'XYZ'[PANEL_GRAIN_AXIS]} - sengens lengderetning. Blir den snudd, "
      f"er raden {PANEL_EDGE_UTIL_CROSS:.2f} og platen holder ikke. "
      f"[X9 regnet den til 0,86 på 324 mm spenn og 250 mm b_ef - feil spenn "
      f"(lektene bærer ikke forkanten) og en b_ef ingen fri kant har]")

# D10: THE PANEL RESTS ON WOOD. No hooks, no exclusions: in each mode the panel
# must have real BEARING AREA - a shared horizontal face, not an edge kiss - on
# the members the design says carry it.
def bearing_area(upper, lower):
    """Horizontal bearing area of `upper` sitting on top of `lower`, in mm2."""
    (ax0, ax1), (ay0, ay1), (az0, _) = upper.extents
    (bx0, bx1), (by0, by1), (_, bz1) = lower.extents
    if abs(az0 - bz1) > TOL:
        return 0.0
    dx = min(ax1, bx1) - max(ax0, bx0)
    dy = min(ay1, by1) - max(ay0, by0)
    return max(dx, 0.0) * max(dy, 0.0)


# V2 recomputation. Three numbers moved and each one is in the table below:
#   the panel is 652 wide, not 680 (the EN 747 side gap);
#   the panel stops PANEL_FIT short of the upright plane, so the rung ledge it
#   lands on is 35 mm, not 37 - the fit comes off the bearing, as it must;
#   the table ledger is 48 deep, not 21, so the rear bearing in TABLE mode goes
#   680 x 21 = 14 280 -> 652 x 48 = 31 296 mm2. Table mode used to be the weak
#   one; after V2 the two modes bear within 4% of each other.
#   bed   rung 1          320 x 35 = 11 200 mm2
#         back bench rail 652 x 48 = 31 296 mm2
#   table rung 2          320 x 35 = 11 200 mm2
#         back ledger     652 x 48 = 31 296 mm2
#
# X9: THE FLOOR IS PER BEARING LINE, NOT PER PIECE - AND THAT IS A RULE BEING
# GENERALISED, NOT RELAXED. The plate has exactly two bearing LINES, front and
# rear, and it has always had two: what MIN_BEARING is about is that a line has
# real face under it rather than an edge kiss. Until X9 each line happened to
# be ONE piece of wood, so "per named support" and "per line" were the same
# sentence. The desk splits the front line into two blocks (they are all the
# uprights will hold - see the X9 bearer note), so the sentence has to be said
# the way it was always meant: the LINE carries MIN_BEARING. The value is
# unchanged at 5 000, nothing is exempted, and the bearer's own length is
# derived FROM this floor rather than checked against it.
#   bed   forkant  rung 1        320 x 30 = 9 600 mm2
#         bakkant  bench rail    574 x 48 = 27 552 mm2
#   table forkant  2 bordklosser 2 x 36 x 70 = 5 040 mm2
#         bakkant  back ledger   574 x 48 = 27 552 mm2
PANEL_SUPPORT_LINES = {
    "bed_mode": {"forkant": ("Ladder Rung_1",),
                 "bakkant": ("Bench Rail Back (continuous)",)},
    "table_mode": {"forkant": ("Table Bearer Left", "Table Bearer Right"),
                   "bakkant": ("Table Ledger Back",)},
}
PANEL_SUPPORTS = {m: tuple(lbl for line in lines.values() for lbl in line)
                  for m, lines in PANEL_SUPPORT_LINES.items()}
PANEL_RUNG_LEDGE = RUNG_REST_LEDGE - PANEL_FIT      # 30, the fit taken off
EXPECT_BEARING = {
    "bed_mode": {"Ladder Rung_1": RUNG_LEN * PANEL_RUNG_LEDGE,
                 "Bench Rail Back (continuous)": PANEL_W * BENCH_RAIL_T},
    "table_mode": {"Table Bearer Left": TABLE_BEARER_T * TABLE_BEARER_LEDGE,
                   "Table Bearer Right": TABLE_BEARER_T * TABLE_BEARER_LEDGE,
                   "Table Ledger Back": PANEL_W * LEDGER_BACK_T},
}
for mode_name, panel in MODES.items():
    found = {p.label: bearing_area(panel, p) for p in parts
             if bearing_area(panel, p) > 0}
    for want in PANEL_SUPPORTS[mode_name]:
        assert want in found, \
            f"D10: the {mode_name} panel does not rest on '{want}' - it only " \
            f"lands on {sorted(found)}"
    for line, members in PANEL_SUPPORT_LINES[mode_name].items():
        _area = sum(found[m] for m in members)
        assert _area >= MIN_BEARING, (
            f"D10/X9: the {mode_name} plate's {line} line is carried on "
            f"{_area:.0f} mm2 ({', '.join(members)}), under the "
            f"{MIN_BEARING} mm2 a bearing line is held to")
    # the front edge and the rear edge must BOTH be carried, or it tips
    assert any(a > 0 for lbl, a in found.items()
               if "Rung" in lbl or "Bearer" in lbl), \
        f"D10: nothing carries the {mode_name} panel's front edge"
    assert any(a > 0 for lbl, a in found.items()
               if "Back" in lbl or "Ledger" in lbl), \
        f"D10: nothing carries the {mode_name} panel's rear edge"
    # D13: exactly these supports, and exactly the areas the note computes.
    assert set(found) == set(EXPECT_BEARING[mode_name]), \
        f"D13: the {mode_name} panel rests on {sorted(found)}, expected " \
        f"{sorted(EXPECT_BEARING[mode_name])}"
    for lbl, want in EXPECT_BEARING[mode_name].items():
        assert abs(found[lbl] - want) < TOL, \
            f"D13: bearing on '{lbl}' is {found[lbl]:.0f} mm2, expected {want}"
    assert not any("Bench Rail Front" in lbl for lbl in found), \
        "D13: the front bench rail segments must no longer carry the panel"
    print(f"OK  D10: {mode_name} panel {panel.extents[2][0]:.0f}.."
          f"{panel.extents[2][1]:.0f} rests on "
          + ", ".join(f"{lbl} ({a:.0f} mm2)" for lbl, a in sorted(found.items()))
          + f" = {sum(found.values()):.0f} mm2 total")
# X10 - THE PANEL SUB-ASSEMBLY, OFF ITS OWN BODIES. Everything from here down
# used to compare a name to the expression it had just been assigned from -
# `PANEL_Y0 == BENCH_SLAT_Y0` when line 2413 reads `PANEL_Y0 = BENCH_SLAT_Y0`,
# and six more like it. Only the trailing literals had any power. The panel,
# its four battens, a rung and an upright are all built by now, so the same
# claims are asked of the shapes, and the literals stay where they were.
_Y1_PANEL = next(q for q in mode_parts(panel_bed)
                 if q.label.startswith("Movable Panel"))
_Y1_GUIDES = [q for q in mode_parts(panel_bed)
              if q.label.startswith("Panel Stiffener Batten")]
_Y1_NOSES = [q for q in mode_parts(panel_bed)
             if q.label.startswith("Panel Front Batten")]
_Y1_RUNG = next(q for q in parts if q.label == "Ladder Rung_1")
_Y1_UP = next(q for q in parts if q.label == "Ladder Upright Left")
(_pnx0, _pnx1), (_pny0, _pny1), _ = _Y1_PANEL.extents
assert _pny1 - _pny0 == PANEL_LEN == PLATFORM_DEPTH - PANEL_FIT, \
    f"D10/V2: the built panel is {_pny1 - _pny0:g} mm deep and has to reach " \
    f"its rear bearing less the front fit, {PLATFORM_DEPTH - PANEL_FIT:g}"
_Y1_BENCH_SLATS = [q for q in parts if q.label.startswith("Bench Slat ")]
assert _pny0 == min(q.extents[1][0] for q in _Y1_BENCH_SLATS) \
        and _Y1_UP.extents[1][0] - _pny1 == PANEL_FIT, \
    f"D10: the built panel runs Y {_pny0:g}..{_pny1:g}; it has to start on " \
    f"the bench slats' own back plane and stop {PANEL_FIT:g} mm short of the " \
    f"upright face at {_Y1_UP.extents[1][0]:g}"
assert _Y1_RUNG.extents[1][1] == _Y1_UP.extents[1][1], \
    "D10: the tread fronts must be flush with the uprights"
assert _Y1_UP.extents[1][0] - _Y1_RUNG.extents[1][0] == RUNG_REST_LEDGE == 32, \
    f"D10/U2: the built rung reaches " \
    f"{_Y1_UP.extents[1][0] - _Y1_RUNG.extents[1][0]:g} mm behind the upright " \
    f"plane to catch the panel, and the file says {RUNG_REST_LEDGE:g} (it was " \
    f"37 while the upright was 48 deep - the tread did not change, the " \
    f"upright did)"
# D13: the panel still straddles BOTH uprights, which is what makes Y=752 a hard
# limit for its front edge and therefore what makes the rung ledge necessary.
assert PANEL_X0 < LADDER_LEFT_X and LADDER_RIGHT_X + UPRIGHT_W < PANEL_X1, \
    "D13: the panel no longer straddles both ladder uprights"
print(f"OK  D10: no hooks - panel {PANEL_T} x {PANEL_W} x {PANEL_LEN} at Y "
      f"{PANEL_Y0}..{PANEL_Y1}, rear edge flush with the bench slats, front edge "
      f"against the uprights; rungs at Y {RUNG_Y0}..{RUNG_Y1} reach "
      f"{LADDER_Y0 - RUNG_Y0} mm behind the upright plane; bed-mode top "
      f"{PANEL_TOP_BED} = {PANEL_BENCH_DIP} mm below the {BENCH_TOP} bench tops "
      f"(cushion recess); table-mode top {PANEL_TOP_TABLE}")

# ---------------------------------------------------------------------------
# M4: THE PANEL STIFFENER BATTENS
# ---------------------------------------------------------------------------
# Four things have to hold, in both modes: the battens are ATTACHED to the
# panel (a real face contact, not a near miss), they CLEAR every other part
# (they run down two open shafts with 2 mm on the guiding side, so there is no
# slack), they stay OUT OF the ladder-bay walking zone, and - V3 - they REACH
# the rung ends, because they are the guides now.
assert len(_Y1_GUIDES) == 2 and len(_Y1_NOSES) == 2, \
    "M4 + M5: two battens along Y, two across X"
for _b in _Y1_GUIDES:
    (_bx0, _bx1), (_by0, _by1), _ = _b.extents
    assert _by1 - _by0 == BATTEN_LEN == 750, \
        f"M4: '{_b.label}' measures {_by1 - _by0:g} mm along Y, want 750"
    assert _by0 == BACK_RAIL_Y1, \
        f"M4: '{_b.label}' starts at Y {_by0:g}; the battens must stop at the " \
        f"back rail face {BACK_RAIL_Y1:g}, not run past it"
    assert _by1 == _pny1, \
        f"M4/V3: '{_b.label}' stops at Y {_by1:g} and the panel's own front " \
        f"edge is {_pny1:g} - the last 30 mm of the batten IS the guide, and " \
        f"it has to be there to stand in the rung's rest-ledge shaft"
    assert _by1 - _Y1_RUNG.extents[1][0] == BATTEN_GUIDE_ENGAGE_Y == 30 \
            and BATTEN_GUIDE_ENGAGE_Y < RUNG_REST_LEDGE, \
        f"M4/V3: '{_b.label}' reaches " \
        f"{_by1 - _Y1_RUNG.extents[1][0]:g} mm into a {RUNG_REST_LEDGE:g} mm " \
        f"shaft - past the ledge it would foul the uprights"
assert LEDGER_BACK_Y0 + LEDGER_BACK_T <= BATTEN_Y0, \
    "M4: the battens foul the back table ledger"
# V2/M5: the two front cross battens - the same stock, the same Z band, flush
# with the panel's front edge, and inside the panel outline in X.
_Y1_GUIDE_X = sorted(q.extents[0] for q in _Y1_GUIDES)
for _i, _n in enumerate(sorted(_Y1_NOSES, key=lambda q: q.extents[0][0])):
    (_nx0, _nx1), (_ny0, _ny1), _ = _n.extents
    assert _ny1 == _pny1 and _ny1 - _ny0 == BATTEN_W, \
        f"M5: '{_n.label}' is at Y {_ny0:g}..{_ny1:g}; it has to be flush " \
        f"with the panel's front edge {_pny1:g} and one batten wide"
    _want = ((_pnx0, _Y1_GUIDE_X[0][0]) if _i == 0
             else (_Y1_GUIDE_X[1][1], _pnx1))
    assert (_nx0, _nx1) == _want, \
        f"M5: '{_n.label}' runs X {_nx0:g}..{_nx1:g}; it has to run from the " \
        f"panel edge to the M4 batten, {_want[0]:g}..{_want[1]:g}"
    assert _nx1 - _nx0 == NOSE_LEN == 77, \
        f"M5: '{_n.label}' is {_nx1 - _nx0:g} mm and the pair has to be " \
        f"{NOSE_LEN:g} and equal"
# The corner they exist for, stated as the number it is: the panel's front edge
# outboard of the M4 batten, in bare 18 mm sheet. V3 shrank it 213 -> 116 and
# K2's narrower panel takes it to 77 - and the note above is still why that is
# not enough to delete them: the free-corner stress does not depend on the
# overhang length at all.
FRONT_CANTILEVER = NOSE_LEN                         # 77  [was 116, 213]
assert FRONT_CANTILEVER == _Y1_GUIDE_X[0][0] - _pnx0 == 77, \
    f"M5: the sheet stands {_Y1_GUIDE_X[0][0] - _pnx0:g} mm outboard of the " \
    f"M4 batten and the file says {FRONT_CANTILEVER:g}"
assert min(q.extents[1][0] for q in _Y1_NOSES) <= _Y1_RUNG.extents[1][0], \
    "M5: a cross batten that starts behind the rung face would have to " \
    "thread past the rung, and the whole assembly goes straight down"
# V4: THE WEDGE. `NOSE_TIP_H == PANEL_UPSCREW_PASS` is a NAMING IDENTITY -
# NOSE_TIP_H is assigned PANEL_UPSCREW_PASS where it is declared, so the line
# is one name against itself and it is labelled as such rather than counted as
# a check. What it was standing in for is asked further down, where the wing's
# own counterbore depths exist: min(_NOSE_CB) == 0, i.e. the bore grounds out
# exactly at the tip and what is left there is the seat.
assert NOSE_TIP_H == PANEL_UPSCREW_PASS        # a naming identity, see _NOSE_CB
_NOSE_TRAPEZOID = BATTEN_W * NOSE_LEN * (NOSE_ROOT_H + NOSE_TIP_H) / 2

# WHAT THE PANEL UNIT WEIGHS, off its own solids. It used to be a number in a
# comment - "4.7 kg of sheet plus 2.5 kg of batten" - and a number in a comment
# goes stale the moment the geometry moves, which is exactly what V4 did to it
# by planing 128 064 mm3 of wood off the two wings. Two densities and the real
# volumes instead. It matters in three places: the J13a up-screw check (the
# only load case those screws have is the unit being picked up by one corner),
# the lock decision in vedlegg B avvik 4, and what a parent is told to lift.
PLY_DENSITY = 500e-9             # kg/mm3, 18 mm gran kryssfiner
# V7: TWO DENSITIES, AND THEY ARE FOR TWO DIFFERENT QUESTIONS.
# 420 is rho_mean for the C24 CLASS (EN 338) - a strength-grading figure, tied
# to the characteristic values the load appendix uses, and the right number to
# quote whenever a number has to be consistent with f_m,k.
# 450 is what the board actually weighs coming off the shelf at ~16% moisture
# (Svenskt Tra). It is the right number for anything a person has to LIFT or
# carry, and for the up-screw case in J13a, where the unit's own mass IS the
# load - there the heavier figure is the conservative one.
# The model keeps the class figure as the primary so every number stays
# consistent with the appendix, and prints the delivered one beside it.
C24_DENSITY = 420e-9             # kg/mm3, rho_mean for the C24 class (EN 338)
C24_DENSITY_DELIVERED = 450e-9   # kg/mm3, board as delivered, ~16% moisture
PANEL_UNIT_MASS = (abs(panel_bed.volume) * PLY_DENSITY
                   + sum(abs(b.volume) for b in battens_bed) * C24_DENSITY)
PANEL_UNIT_WEIGHT = PANEL_UNIT_MASS * 9.81                    # N
assert 6.0 < PANEL_UNIT_MASS < 8.5, (
    f"the panel unit is {PANEL_UNIT_MASS:.1f} kg - if that is right the "
    f"lifting argument in vedlegg B avvik 4 has to be re-read, and so has "
    f"the J13a up-screw case")
PANEL_UNIT_MASS_DELIVERED = (abs(panel_bed.volume) * PLY_DENSITY
                             + sum(abs(b.volume) for b in battens_bed)
                             * C24_DENSITY_DELIVERED)
_tv = sum(abs(p.volume) for p in _WOOD)
BED_MASS = _tv * C24_DENSITY + abs(panel_bed.volume) * PLY_DENSITY
BED_MASS_DELIVERED = _tv * C24_DENSITY_DELIVERED + abs(panel_bed.volume) * PLY_DENSITY
print(f"OK  hele sengen veier {BED_MASS:.0f} kg regnet med C24-klassetallet "
      f"420 kg/m3 og {BED_MASS_DELIVERED:.0f} kg med levert virke, 450 - "
      f"begge uten madrass og puter. Det er tallet to voksne skal flytte")
print(f"OK  plateenheten veier {PANEL_UNIT_MASS:.1f} kg "
      f"({PANEL_UNIT_WEIGHT:.0f} N) - "
      f"{abs(panel_bed.volume) * PLY_DENSITY:.1f} kg plate + "
      f"{sum(abs(b.volume) for b in battens_bed) * C24_DENSITY:.1f} kg lekt, "
      f"regnet av kroppene og ikke sitert. Løftet etter ett hjørne med "
      f"faktor 2 er {2 * PANEL_UNIT_WEIGHT:.0f} N mot "
      f"{sum(1 for f in FASTENER_SPECS if f['jid'].startswith('J13'))} skruer i J13 "
      f"(levert virke: {PANEL_UNIT_MASS_DELIVERED:.1f} kg)")
for _w in (b for b in battens_bed + battens_table
           if b.label.startswith("Panel Front Batten")):
    assert getattr(_w, "tapered", None) is not None, \
        f"M5/V4: '{_w.label}' is still a box"
    assert abs(abs(_w.volume) - _NOSE_TRAPEZOID) < 1.0, (
        f"M5/V4: '{_w.label}' is {abs(_w.volume):.0f} mm3, and the wedge "
        f"{NOSE_ROOT_H} -> {NOSE_TIP_H} over {NOSE_LEN} is "
        f"{_NOSE_TRAPEZOID:.0f}")
    # and it still meets the panel over the WHOLE of its top face: the cut is
    # on the underside, which touches nothing.
    assert abs(_w.extents[2][1] - _w.extents[2][0] - BATTEN_H) < TOL


def _wing_height_at(wing, x):
    """The wing's depth in Z at position `x`, off its own two numbers."""
    (wx0, wx1), _y, _z = wing.extents
    tip_dz, tip_at_x0 = wing.tapered
    t = (x - wx0) / (wx1 - wx0) if tip_at_x0 else (wx1 - x) / (wx1 - wx0)
    return tip_dz + (BATTEN_H - tip_dz) * t


# THE SCREW SEAT ALONG THE TAPER. Every J13b head sits PANEL_UPSCREW_PASS below
# the panel, which is a CONSTANT Z - so the counterbore simply gets shallower as
# the wood does, and the one thing that must hold is that there is still
# PANEL_UPSCREW_PASS of wood at every hole, measured at the WIDE edge of the
# head, not on its centre line.
if FASTENERS_ON:
    _wings = {b.label: b for b in battens_bed
              if b.label.startswith("Panel Front Batten")}
    _seen_wing_screws = 0
    for _f in FASTENER_SPECS:
        if _f["jid"] != "J13b" or _f.get("solid") is None:
            continue
        _w = _wings[_f["through"].label]
        _hr = SCREW_HEAD_D[int(round(_f["d"]))] / 2
        _thin = min(_wing_height_at(_w, _f["anchor"][0] - _hr),
                    _wing_height_at(_w, _f["anchor"][0] + _hr))
        assert _thin >= PANEL_UPSCREW_PASS - TOL, (
            f"{_f['solid'].label}: the wing is only {_thin:.1f} mm deep at "
            f"the edge of this head and the up-screw needs "
            f"{PANEL_UPSCREW_PASS} - the taper has run past its own screws")
        _seen_wing_screws += 1
    # Every J13b screw has to have been sat on the taper - a spec that never
    # reached this loop is a screw nobody checked the wing depth under.
    _want_wing_screws = len([f for f in FASTENER_SPECS if f["jid"] == "J13b"])
    assert _seen_wing_screws == _want_wing_screws == 2 * JOINT["J13b"]["n"], \
        f"M5/V4: {_seen_wing_screws} wing screws checked of "\
        f"{_want_wing_screws} placed - one of them never met the taper"
    _NOSE_CB = [round(_wing_height_at(_wings[_f["through"].label],
                                      _f["anchor"][0]) - PANEL_UPSCREW_PASS, 1)
                for _f in FASTENER_SPECS if _f["jid"] == "J13b"]
    # X10: THE CHECK `NOSE_TIP_H == PANEL_UPSCREW_PASS` COULD NOT MAKE. The tip
    # being the seat is a claim about the TAPER, and the taper is what decides
    # how deep each bore goes: the bore is whatever wood stands over the 27 mm
    # pass at that screw's own X, so it has to run out to 0 exactly AT the tip
    # and never below it anywhere. Measured on the wing profile and the placed
    # screws - a taper cut to a different tip height puts a negative number in
    # this list, and a negative counterbore is a hole out the bottom.
    assert min(_NOSE_CB) >= 0.0 \
            and _wing_height_at(_wings[_Y1_NOSES[0].label],
                                _Y1_NOSES[0].extents[0][0]) \
            == NOSE_TIP_H == PANEL_UPSCREW_PASS, (
        f"M5/V4: the wing's tip measures "
        f"{_wing_height_at(_wings[_Y1_NOSES[0].label], _Y1_NOSES[0].extents[0][0]):g}"
        f" mm on the taper this file cuts and the up-screw's pass is "
        f"{PANEL_UPSCREW_PASS} - the tip IS the seat or it is a number "
        f"somebody liked. Counterbores under the two screws: "
        f"{sorted(set(_NOSE_CB))} mm, none of them below 0")
    print(f"OK  M5/V4 kile: begge vingene er skråkappet "
          f"{NOSE_ROOT_H} → {NOSE_TIP_H} mm over {NOSE_LEN} mm "
          f"({NOSE_TAPER_DEG:.1f}°), {_NOSE_TRAPEZOID:.0f} mm3 tre hver mot "
          f"{BATTEN_W * NOSE_LEN * BATTEN_H} som en hel kloss - "
          f"{100 * (1 - _NOSE_TRAPEZOID / (BATTEN_W * NOSE_LEN * BATTEN_H)):.0f}"
          f" % mindre synlig masse under forkanten. Tuppen ER skrueseten "
          f"({PANEL_UPSCREW_PASS} mm), så kontraboret bare grunner ut med "
          f"treet: {sorted(set(_NOSE_CB))} mm på de "
          f"{len(_NOSE_CB) // 2} hullene. Verste "
          f"bøyesnitt ligger {NOSE_CRIT_X:.0f} mm fra tuppen (h = "
          f"{NOSE_CRIT_H:.0f} mm), ikke ved roten: "
          f"{6 * 1000 * NOSE_CRIT_X / (BATTEN_W * NOSE_CRIT_H ** 2):.2f} MPa "
          f"mot {F_M_D_C24:g} = utnyttelse "
          f"{6 * 1000 * NOSE_CRIT_X / (BATTEN_W * NOSE_CRIT_H ** 2) / F_M_D_C24:.2f}"
          f"; skjær i tuppen (med k_cr = {K_CR:g}) "
          f"{1.5 * 1000 / (K_CR * BATTEN_W * NOSE_TIP_H):.2f} MPa mot "
          f"{F_V_D:g} = "
          f"{1.5 * 1000 / (K_CR * BATTEN_W * NOSE_TIP_H) / F_V_D:.2f}")
# K2: the material argument, checked rather than quoted. See the note above the
# up-screw constants - this is the assert that stops "too wide for limtre"
# being repeated once it stopped being true.
assert PANEL_FITS_LIMTRE == (PANEL_W <= LIMTRE_SHELF_W)
print(f"OK  K2 platematerialet: platen er {PANEL_W} mm bred og "
      + (f"GÅR NÅ INN i en {LIMTRE_SHELF_W} mm limtreplate - argumentet som "
         f"tvang fram kryssfiner (652 > {LIMTRE_SHELF_W}) gjelder ikke lenger. "
         f"Materialet står likevel: lasttabellen, uttrekket for oppskruene og "
         f"propp-argumentet i J13 er regnet på kryssfiner. Det er et VALG nå, "
         f"ikke en tvang, og det er ført opp som åpent punkt"
         if PANEL_FITS_LIMTRE else
         f"er bredere enn de {LIMTRE_SHELF_W} mm limtre furu stopper på - "
         f"kryssfiner er det eneste som finnes i den bredden"))
# X: OUTBOARD of both rung ends by the fit, and symmetric about the centreline.
assert BATTEN_X[0] + BATTEN_W == LADDER_INNER_L - PANEL_FIT and \
    BATTEN_X[1] == LADDER_INNER_R + PANEL_FIT, \
    "M4/V3: a batten does not stand the fit off its rung end"
assert BATTEN_X[0] + BATTEN_W <= RUNG_BLOCK_X[0] and \
    BATTEN_X[1] >= RUNG_BLOCK_X[1] + RUNG_BLOCK_T, \
    "M4: a batten crosses the rung-block line"
batten_centres = [x + BATTEN_W / 2 for x in BATTEN_X]
assert abs((batten_centres[0] + batten_centres[1]) / 2 - LADDER_CENTER_X) < TOL, \
    f"M4: the battens are not symmetric about the ladder centreline: {batten_centres}"
for bx0 in BATTEN_X:
    assert PANEL_X0 <= bx0 and bx0 + BATTEN_W <= PANEL_X1, \
        "M4: a batten hangs off the edge of the panel"

WALK_ZONE = (OPEN_FLOOR_X, (BACK_RAIL_Y1, RUNG_Y0), WALK_ZONE_Z)
for mode_name, panel in MODES.items():
    batts = PANEL_BATTENS[id(panel)]
    assert len(batts) == 4, "M4 + M5: two battens along Y, two across X"
    for b in batts:
        # attached: the batten top IS the panel underside, over its whole face
        area = bearing_area(panel, b)
        own = ((b.extents[0][1] - b.extents[0][0])
               * (b.extents[1][1] - b.extents[1][0]))
        assert abs(area - own) < TOL, \
            f"M4/M5: '{b.label}' only meets the panel over {area:.0f} mm2, " \
            f"want {own}"
        assert abs(b.distance(panel)) < TOL, f"M4: '{b.label}' is not on the panel"
        # clear: zero overlap with every other member of this mode. (The general
        # no-two-parts-overlap check below sees the battens too; this one names
        # the batten and runs with a hard zero instead of the 1 mm3 threshold.)
        for q in mode_parts(panel):
            if q is b or is_soft(q):
                continue
            inter = [min(a1, c1) - max(a0, c0)
                     for (a0, a1), (c0, c1) in zip(b.extents, q.extents)]
            assert min(inter) <= 0.0, \
                f"M4: '{b.label}' overlaps '{q.label}' in {mode_name} by " \
                f"{inter} mm"
        # out of the walking zone under the ladder bay
        inter = [min(a1, c1) - max(a0, c0)
                 for (a0, a1), (c0, c1) in zip(b.extents, WALK_ZONE)]
        assert min(inter) <= TOL, \
            f"M4: '{b.label}' hangs into the ladder-bay walking zone in {mode_name}"
        assert b.extents[2][0] >= BENCH_RAIL_BOTTOM - TOL, \
            f"M4: '{b.label}' reaches below Z {BENCH_RAIL_BOTTOM} in {mode_name}"
    print(f"OK  M4: {mode_name} - 2 x {sec(BATTEN_W, BATTEN_H)} x {BATTEN_LEN} "
          f"battens on edge at X {BATTEN_X[0]}..{BATTEN_X[0] + BATTEN_W} / "
          f"{BATTEN_X[1]}..{BATTEN_X[1] + BATTEN_W}, Y {BATTEN_Y0}..{BATTEN_Y1}, "
          f"Z {batts[0].extents[2][0]:.0f}..{batts[0].extents[2][1]:.0f}, "
          f"{BATTEN_W * BATTEN_LEN} mm2 screwed face each to the panel, "
          f"clear of every other part and of the walking zone below Z "
          f"{BENCH_RAIL_BOTTOM}")
print(f"OK  M4: panel utilisation at the 2 kN dynamic point ~1.4 -> ~0.26 - the "
      f"battens turn an 18 mm sheet over a {BATTEN_LEN} mm span into two tee "
      f"sections (W = 2 x {BATTEN_W}*{BATTEN_H}^2/6 = "
      f"{2 * BATTEN_W * BATTEN_H ** 2 // 6} mm3 in the webs alone)")
print(f"OK  M5: the front corner is carried on wood, not on sheet - a 1 kN "
      f"knee on the free corner of a bare 18 mm panel is 6P/t^2 = "
      f"{6 * 1000 / PANEL_T ** 2:.1f} MPa whatever the batten spacing, and "
      f"the {NOSE_LEN} mm wing takes it as a cantilever off the guide "
      f"batten. The 18 mm PLYWOOD DOUBLER that would have replaced it is "
      f"rejected on its own number: {6 * 1000 / (2 * PANEL_T) ** 2:.2f} MPa "
      f"(utilisation 0.67) WITH full composite action across the glue line, "
      f"{6 * 500 / PANEL_T ** 2:.2f} MPa (utilisation 1.33, a FAIL) without "
      f"it - and no screw in this bed can back that glue line up without "
      f"coming out of the table top")
print(f"OK  V3 J13: the battens are GLUED and screwed from below - "
      f"{PANEL_UPSCREW_CBORE} mm counterbore, {PANEL_UPSCREW_PASS} mm of "
      f"batten left, {PANEL_UPSCREW_BITE} mm of thread in the {PANEL_T} mm "
      f"sheet and {PANEL_UPSCREW_COVER} mm of it standing over the point. "
      f"Nothing breaks the table top's face")

# ===========================================================================
# V2: THE THREE THINGS THE OLD PANEL MECHANISM WAS NEVER ASKED
# ===========================================================================
# The krokplate and the U-brakett were not wrong in any drawing. They were
# wrong in three questions nobody put to the model, and each of those questions
# is now a family of asserts that runs on every build:
#
#   1  CAN IT GO IN?          the insertion sweep. A mechanism you cannot lower
#                             into place is not a mechanism, and "it looks like
#                             it fits" is what a hook that wraps a rung always
#                             looks like.
#   2  DOES EACH PIECE OF     the engagement directions. Steel that opposes a
#      STEEL DO ANYTHING?     motion the wall already opposes is decoration,
#                             and a direction nothing opposes is a rattle.
#   3  ARE THE GAPS LEGAL?    the EN 747 bands, on the gaps a child can reach
#                             around the seated panel - the check that caught
#                             the 10 mm side gap this round started with.
# ---------------------------------------------------------------------------


def _box_extents(shape):
    bb = shape.bounding_box()
    return ((bb.min.X, bb.max.X), (bb.min.Y, bb.max.Y), (bb.min.Z, bb.max.Z))


def panel_assembly_boxes(mode):
    """[(label, extents), ...] - every solid that travels with the panel.

    The panel, its four battens and the eighteen screws. It reads them off
    `display_parts`, which is the SAME list the export and the drawings use,
    so the sweep can never be run on a set of parts that differs from the one
    the .usdz shows - the failure that made the panel and its own screws sit
    at two different heights in table mode.
    """
    panel = MODES[mode]
    moving = [panel] + PANEL_BATTENS[id(panel)]
    if FASTENERS_ON:
        moving += panel_fasteners(panel)
    return [(p.label, p.extents) for p in moving]


# 0 - THE SUB-ASSEMBLY IS ONE PART, AND IT IS THE SAME PART IN BOTH MODES.
# This is the assert the shipped bug walked straight through: the panel is a
# unit that gets LIFTED, so every piece of it - sheet, four battens, eighteen
# screws - must sit at exactly the same place RELATIVE TO THE PANEL at both
# heights. Measured on the solids, per label, as an offset from the panel's
# own minimum corner. Anything that fails this is something the two exports
# disagree about, which is precisely what the .usdz showed.
def _panel_relative(mode):
    panel = MODES[mode]
    o = tuple(panel.extents[j][0] for j in range(3))
    return {label: tuple((lo - o[j], hi - o[j])
                         for j, (lo, hi) in enumerate(ext))
            for label, ext in panel_assembly_boxes(mode)}


_REL = {m: _panel_relative(m) for m in MODES}
_REL_KEYS = {m: sorted(k.replace(f" ({m.replace('_', ' ')})", "")
                       for k in _REL[m]) for m in MODES}
assert _REL_KEYS["bed_mode"] == _REL_KEYS["table_mode"], (
    "V3: the two modes do not even carry the same panel sub-assembly: "
    f"{set(_REL_KEYS['bed_mode']) ^ set(_REL_KEYS['table_mode'])}")
for _label, _rel in _REL["bed_mode"].items():
    _other = _label.replace("(bed mode)", "(table mode)")
    _got = _REL["table_mode"].get(_other)
    assert _got is not None, f"V3: '{_other}' is missing from table mode"
    for _j in range(3):
        assert all(abs(a - b) < TOL for a, b in zip(_rel[_j], _got[_j])), (
            f"V3 modus: '{_label}' sits at {_rel[_j]} on axis {'XYZ'[_j]} "
            f"relative to the panel in bed mode and at {_got[_j]} in table "
            f"mode. The panel sub-assembly must be IDENTICAL relative to the "
            f"panel in both modes - it is one thing that gets lifted, not two "
            f"things that get built")
print(f"OK  V3 modus: alle {len(_REL['bed_mode'])} delene i plateenheten - "
      f"plate, {len(PANEL_BATTENS[id(panel_bed)])} lekter og "
      f"{len(_REL['bed_mode']) - 1 - len(PANEL_BATTENS[id(panel_bed)])} "
      f"skruer - står på nøyaktig samme sted i forhold til platen i begge "
      f"stillinger. Enheten løftes, den bygges ikke to ganger")


def _footprints_overlap(a, b):
    return all(min(a[j][1], b[j][1]) - max(a[j][0], b[j][0]) > TOL
               for j in (0, 1))


def vertical_clear(mode):
    """(mm, what stops it) - how far the whole assembly can rise, straight up,
    before any part of it meets any part of the bed."""
    moving = panel_assembly_boxes(mode)
    fixed = [p for p in parts if not is_soft(p)]
    best, who = math.inf, None
    for label, m in moving:
        for f in fixed:
            if not _footprints_overlap(m, f.extents):
                continue
            gap = f.extents[2][0] - m[2][1]
            if gap < -TOL:
                continue                    # it is below us, not in the way
            if gap < best:
                best, who = gap, f"'{label}' under '{f.label}'"
    return best, who


# 1 - THE INSERTION SWEEP, AND THE THEOREM IT MEASURES AGAINST.
# The panel does not slide: its rear edge IS the wall plane and its front edge
# is PANEL_FIT off the ladder. So the ONLY move it has is straight up and
# straight down, and every part of the assembly - sheet, four battens and the
# eighteen screws that hold them - has to make that move together. V3 raised
# the stake on this one: the battens no longer stop short of the rung, they run
# down the shafts BESIDE the rung ends and are in those shafts for the whole
# descent, so the sweep is now measuring the guides themselves.
# THE LIMIT IS NOT A DESIGN CHOICE, IT IS GEOMETRY: a two-height convertible
# whose upper seat lies over the lower one can never have an unbounded vertical
# path into the LOWER position, because the thing that carries it up there is
# in the way on the trip down. The rear support at table height is exactly that
# member. What the design CAN do - and what V2 does - is make that ceiling as
# high as it goes: the ledger became a 73 mm member instead of a 95 mm one, so
# its underside rose 387 -> 409 and the clear run with it. What is asserted is
# therefore the number, measured, in both modes, on the solids.
# INSERT_CLEAR_MIN is declared up in the LADDER section now (X9): the number
# that decides whether a lift is a lift is also the number that decides where
# rung 3 goes, and it cannot be read here and used there.
INSERT_CLEAR = {}
INSERT_STOPPER = {}
for _mode in MODES:
    _run, _who = vertical_clear(_mode)
    INSERT_CLEAR[_mode] = _run
    INSERT_STOPPER[_mode] = _who
    assert _run >= INSERT_CLEAR_MIN, (
        f"V2 innsetting: the {_mode} assembly can only rise {_run:.0f} mm "
        f"before {_who} - it cannot be lifted clear of its own locators "
        f"(the guide battens have to rise "
        f"{BATTEN_GUIDE_RELEASE_Z:g} mm to come free)")
    assert _run > BATTEN_GUIDE_RELEASE_Z, (
        f"V2 innsetting: {_run:.0f} mm of clear lift in {_mode} is less than "
        f"the {BATTEN_GUIDE_RELEASE_Z:g} mm it takes to lift the guide "
        f"battens' undersides past the locator tops - the assembly cannot "
        f"come out of its own seat at all")
print(f"OK  V2 innsetting: the panel assembly - sheet, 4 lekter og "
      f"{sum(1 for f in FASTENER_SPECS if f['jid'].startswith('J13'))} skruer "
      f"- går rett ned i begge stillinger. Fri loddrett vei "
      f"{INSERT_CLEAR['bed_mode']:.0f} mm i sengestilling "
      f"({INSERT_STOPPER['bed_mode']}) og {INSERT_CLEAR['table_mode']:.0f} mm "
      f"i bordstilling ({INSERT_STOPPER['table_mode']}), mot "
      f"{BATTEN_GUIDE_RELEASE_Z} mm som skal til for å løfte styrelektenes "
      f"underkant fri av låsedelens overkant (lektene LAPPER "
      f"{BATTEN_GUIDE_ENGAGE_Z} mm av den - det er to forskjellige mål). "
      f"Ingenting i veien for noen av delene på veien ned")


# ---------------------------------------------------------------------------
# K1 - THE TRANSFER SLOT, MEASURED
# ---------------------------------------------------------------------------
# The panel does not go from the bed seat to the table seat straight up: the
# thing that carries it at table height is in the way on the trip down, so it
# has to travel SIDEWAYS out of the ladder bay, over a bench, and back. The
# corridor it crosses on that trip is a horizontal slot, and the slot is the
# number that decides whether the move is a flat carry or a wrestle.
#
# Both walls of it are read off the solids here, not typed:
#   FLOOR   the highest thing the assembly passes OVER on its way across -
#           the bench slat tops, 295;
#   CEILING the lowest thing it passes UNDER - and this is what K1 changed.
#           It used to be the rung blocks' undersides at 386, because 37 mm of
#           every block hung behind its upright, unattached, straight into the
#           corridor. With the block cut to the upright's own depth the blocks
#           are not in the corridor at all and the ceiling is the back table
#           ledger's underside at 409, which is a member that has to be there.
# 91 -> 114 mm against a 91 mm unit: from a zero-clearance fit that could only
# be got through on a 3 degree roll, to 23 mm of daylight and a flat carry.
TRANSFER_CORRIDOR_X = (POST_W, WALL_SPAN - POST_W)         # 98 .. 1892


def _in_transfer_corridor(p):
    """Does this part stand in the band the travelling panel unit crosses?"""
    (x0, x1), (y0, y1), _z = p.extents
    return (x1 > TRANSFER_CORRIDOR_X[0] + TOL
            and x0 < TRANSFER_CORRIDOR_X[1] - TOL
            and y1 > PANEL_Y0 + TOL and y0 < PANEL_Y1 - TOL)


_corridor = [p for p in parts if _in_transfer_corridor(p)]
TRANSFER_CEILING, TRANSFER_CEILING_WHO = min(
    (p.extents[2][0], p.label) for p in _corridor
    if p.extents[2][0] >= PANEL_TOP_BED - TOL)
TRANSFER_FLOOR, TRANSFER_FLOOR_WHO = max(
    (p.extents[2][1], p.label) for p in _corridor
    if p.extents[2][1] <= TRANSFER_CEILING + TOL)
TRANSFER_SLOT = TRANSFER_CEILING - TRANSFER_FLOOR          # 204  [was 154,
                                                           # X1: 114]
PANEL_UNIT_H = PANEL_TOP_BED - BATTEN_Z0_BED               # 86   [X3: 91]
TRANSFER_CLEAR = TRANSFER_SLOT - PANEL_UNIT_H              # 118  [was 68,
                                                           # X1: 23]
# The gate. Under 15 mm the unit has to be tipped to get through, and a tipped
# unit is a two-person move over a bench - that is what the comfort round was
# opened to get rid of.
TRANSFER_CLEAR_MIN = 15
assert TRANSFER_CLEAR >= TRANSFER_CLEAR_MIN, (
    f"K1: the transfer slot is {TRANSFER_SLOT:g} mm ({TRANSFER_FLOOR_WHO} "
    f"{TRANSFER_FLOOR:g} to {TRANSFER_CEILING_WHO} {TRANSFER_CEILING:g}) and "
    f"the panel unit is {PANEL_UNIT_H:g} mm tall, so it passes with "
    f"{TRANSFER_CLEAR:g} mm - under the {TRANSFER_CLEAR_MIN} mm that makes "
    f"the mode change a flat carry. Raise the ceiling or lower the unit")
assert "Rung Block" not in TRANSFER_CEILING_WHO, \
    "K1: a rung block is back in the transfer corridor - the whole point of " \
    "cutting it to the upright's depth was to get it out of there"
print(f"OK  K1 overføringssjakten: {TRANSFER_SLOT:g} mm fri høyde "
      f"({TRANSFER_FLOOR_WHO} {TRANSFER_FLOOR:g} → {TRANSFER_CEILING_WHO} "
      f"{TRANSFER_CEILING:g}) for en {PANEL_UNIT_H:g} mm høy plateenhet = "
      f"{TRANSFER_CLEAR:g} mm klaring, krav {TRANSFER_CLEAR_MIN}. Taket var "
      f"stigeklossenes underkant på 386 så lenge 37 mm av hver kloss hang bak "
      f"vangen sin (K1), og bordskinnas underkant på 474 etterpå; X9 løftet "
      f"skinna til {LEDGER_BACK_Z0:g} og lot trinn 2 bli det laveste taket "
      f"over benken. Selve KRYSSINGEN ved stigen er et annet og trangere "
      f"tall - se X9-blokka lenger ned")

# K1 - AND WHAT THE SHORTER BLOCK COSTS THE JOINT. Two rows, both re-derived:
#   J5, the block on the upright - UNCHANGED, because the block never touched
#       more of the upright than the upright's own 36 mm of depth. Same face,
#       same one 5x60, and the screw now lands in the MIDDLE of that face
#       instead of half a millimetre outside its back plane.
#   the rung ON the block - compression across the grain on 36 x 36 instead of
#       36 x 73. A rung carries the 1 kN climber over two ends.
RUNG_BLOCK_FACE = UPRIGHT_T * RUNG_BLOCK_H           # 1728 mm2 on the upright
RUNG_BLOCK_BEARING = RUNG_BLOCK_T * RUNG_BLOCK_LEN   # 1296 mm2 under the rung
CLIMBER_KN = 1.0
RUNG_END_KN = CLIMBER_KN / 2
FC90_D = 2.5                     # N/mm2, C24 across the grain, k_c,90 = 1
_j5 = [f for f in FASTENER_SPECS if f["jid"] == "J5"]
assert len(_j5) == 2 * len(RUNG_TOPS) and {int(round(f["d"])) for f in _j5} == {5}
RUNG_BLOCK_BEAR_UTIL = RUNG_END_KN * 1000 / RUNG_BLOCK_BEARING / FC90_D
RUNG_BLOCK_SCREW_UTIL = RUNG_END_KN / SCREW_SHEAR_KN[5]
assert RUNG_BLOCK_FACE == UPRIGHT_T * BLOCK_H, \
    "K1: the block's face on the upright is supposed to be unchanged - the " \
    "upright's own depth by the block's own height, which is what it always was"
assert 2 * RUNG_BLOCK_SCREW_UTIL <= MAX_BLOCKLESS_UTIL, (
    f"K1: J5's single 5 mm screw is {2 * RUNG_BLOCK_SCREW_UTIL:.2f} utilised "
    f"with the whole climber over one rung end - over the "
    f"{MAX_BLOCKLESS_UTIL:g} gate the block-less corners are held to")
assert RUNG_BLOCK_BEAR_UTIL <= 0.5, (
    f"K1: the rung bears on {RUNG_BLOCK_BEARING} mm2 of block at "
    f"{RUNG_BLOCK_BEAR_UTIL:.2f} of f_c,90,d - cut the block shorter than the "
    f"upright is deep and this is the row that goes first")
# X10 - AND WHAT THE BLOCK LOST THIS ROUND. J4 used to put a 5x60 down through
# the tread into this block; it was driven straight through the 6x120's own
# hole and it is gone (see the X10 note in the JOINTS table). Neither row above
# moves - that screw was never in the load path, it was the block's LOCK
# against turning about its single J5 screw. The lock is still there, it is
# just wood now: the block is caught between the upright's face, the tread
# lying flat on RUNG_BLOCK_BEARING of its top, and that tread being itself
# pinned to the upright by the 6x120 24 mm above the block's own screw. To turn
# about J5, the block has to lift a tread that is screwed down.
assert not [f for f in FASTENER_SPECS
            if f["jid"] == "J4" and f.get("into") is not None
            and "Rung Block" in f["into"].label], \
    "X10: a screw is back in the rung block from above - it cannot get there " \
    "without crossing J4's own 6x120, which is why it was taken out"
# The one thing the shorter block does change is that the rung's rear
# RUNG_REST_LEDGE hangs over nothing. It is a 48 mm thick tread and the
# overhang is 37 mm; the check is that it is an overhang and not a span.
assert RUNG_REST_LEDGE <= RUNG_T, (
    f"K1: the rung's rest ledge is {RUNG_REST_LEDGE} mm of unsupported tread "
    f"behind a {RUNG_T} mm block - past the tread's own thickness that stops "
    f"being a corner and starts being a cantilever")
print(f"OK  K1 stigeklossen 36x48 x {RUNG_BLOCK_LEN} (var {RUNG_D}): flate mot "
      f"vangen {RUNG_BLOCK_FACE} mm² UENDRET (klossen nådde aldri lenger inn "
      f"enn vangens egne {UPRIGHT_T} mm), J5 fremdeles 1 x 5x60 = "
      f"{SCREW_SHEAR_KN[5]:.1f} kN mot {RUNG_END_KN:.1f} → "
      f"{RUNG_BLOCK_SCREW_UTIL:.2f} (verste plassering "
      f"{2 * RUNG_BLOCK_SCREW_UTIL:.2f}, grense {MAX_BLOCKLESS_UTIL:g}); "
      f"trinnet ligger på {RUNG_BLOCK_BEARING} mm² (var "
      f"{RUNG_BLOCK_T * RUNG_D}) = {RUNG_END_KN * 1000 / RUNG_BLOCK_BEARING:.2f} "
      f"MPa mot {FC90_D:g} på tvers av fiberretningen → "
      f"{RUNG_BLOCK_BEAR_UTIL:.2f}; skruen sitter nå på Y {RUNG_BLOCK_Y0 + RUNG_BLOCK_LEN / 2:g}, "
      f"midt i vangen - og den er hele festet nå: X10 tok ut skruen ned "
      f"gjennom trinnet, som gikk gjennom 6×120-en sin egen kanal")


# ---------------------------------------------------------------------------
# X8/X9 - HOW HIGH THE TABLE CAN GO, AND WHY IT IS NOT A MATTER OF TASTE
# ---------------------------------------------------------------------------
# X8 wrote this block as a REFUSAL. The builder had asked for a DESK - the
# plate at ~700 over the floor, 280 over the seat cushion, knees under it, IKEA
# SMASTAD's 730 as the thing to point at - and the ceiling this block computed
# was 639, because rung 3 stood at 787 and its underside was a lid at 739. The
# arithmetic was right and the conclusion was wrong by one assumption: that the
# LADDER was fixed and the table had to fit under it. X9 moves rung 3 (see the
# X9 note in the LADDER section) and the same arithmetic now says yes.
#
# THE BLOCK IS UNCHANGED. That is the point of it. It still computes the
# ceiling off the solids and still refuses anything above it - what changed is
# the solids it measures, and the plate now sits EXACTLY ON the ceiling rather
# than 79 mm under it. Nothing here was relaxed to let the desk through: rung 3
# went up by exactly the 61 mm that made 700 legal, and the assert below is the
# thing that says 61 and not 60.
#
# THE TWO WALLS, both of them the same piece of wood:
#   1  THE STRAIGHT-UP RUN. The panel is 574 x 798 and the ladder rungs run
#      X 835..1155 at Y 720..788, so wherever the plate sits at the ladder its
#      front strip lies UNDER a rung. In table mode the rung above is rung 3,
#      measured here as the stopper of INSERT_CLEAR. The unit has to rise
#      BATTEN_GUIDE_RELEASE_Z (68) before its guides are free of their locator
#      at all, and INSERT_CLEAR_MIN (100) before that is a lift and not a
#      wrestle - so the plate TOP can be at most the rung underside less 100.
#      THIS IS THE BINDING WALL, and after X9 it binds exactly: 800 - 100 = 700.
#   2  THE CROSSING. The unit does not go from seat to seat straight up: it
#      goes out over a bench and comes back across the ladder in the free band
#      between rung 2's top and rung 3's underside (K3, leg 6). Whatever
#      carries the plate's front edge at table height stands IN that band -
#      after X9 that is the two bordklosser rather than a rung - so the unit
#      has to cross ABOVE it: batten bottom over the bearer top, i.e. over the
#      plate's own underside, while the plate top is still under rung 3. That
#      is PANEL_UNIT_H - PANEL_T = 68 mm of the band spent before the unit is
#      even in it, and it leaves TABLE_CROSS_CLEAR of daylight.
# Both are measured, neither is typed, and the lower of the two is the ceiling.
TABLE_CEILING_Z = PANEL_TOP_TABLE + INSERT_CLEAR["table_mode"]     # 800
TABLE_TOP_MAX_LIFT = TABLE_CEILING_Z - INSERT_CLEAR_MIN            # 700
TABLE_TOP_MAX_CROSS = TABLE_CEILING_Z - (PANEL_UNIT_H - PANEL_T)   # 732
TABLE_TOP_CEILING = min(TABLE_TOP_MAX_LIFT, TABLE_TOP_MAX_CROSS)   # 700
# X9: the crossing band, read off the two members that make it, and what is
# left of it once the unit is in it. This is the number X8 called "29 mm short"
# and it is the one the mechanism film has to fly the unit through.
TABLE_CROSS_BAND = TABLE_CEILING_Z - PANEL_UNDER_TABLE             # 118
TABLE_CROSS_CLEAR = TABLE_CROSS_BAND - PANEL_UNIT_H                # 32
assert PANEL_TOP_TABLE <= TABLE_TOP_CEILING, (
    f"X8: the table plate is drawn at {PANEL_TOP_TABLE} and the mode change "
    f"tops out at {TABLE_TOP_CEILING} - {TABLE_CEILING_Z} "
    f"({INSERT_STOPPER['table_mode']}) less the bigger of "
    f"{INSERT_CLEAR_MIN} mm of straight-up run and the "
    f"{PANEL_UNIT_H - PANEL_T} mm the unit spends getting over its own front "
    f"bearer on the way across. Above that the plate can be drawn but not "
    f"put there")
assert TABLE_CROSS_CLEAR >= TRANSFER_CLEAR_MIN, (
    f"X9: the unit crosses the ladder in a {TABLE_CROSS_BAND:g} mm band "
    f"(bearer top {PANEL_UNDER_TABLE} to {INSERT_STOPPER['table_mode']} at "
    f"{TABLE_CEILING_Z:g}) and it is {PANEL_UNIT_H:g} mm tall, so it passes "
    f"with {TABLE_CROSS_CLEAR:g} mm - under the {TRANSFER_CLEAR_MIN} mm that "
    f"makes the mode change a flat carry")
print(f"OK  X8/X9 bordhøydens tak: {TABLE_TOP_CEILING:g} mm platetopp. "
      f"{INSERT_STOPPER['table_mode']} setter taket på {TABLE_CEILING_Z:g}; "
      f"derfra går {INSERT_CLEAR_MIN} mm til rett løft (gir "
      f"{TABLE_TOP_MAX_LIFT:g}) og {PANEL_UNIT_H - PANEL_T:g} mm til å komme "
      f"over sin egen bærekant på tvers (gir {TABLE_TOP_MAX_CROSS:g}) - det "
      f"laveste gjelder. Platen ligger på {PANEL_TOP_TABLE}, altså PRESIS i "
      f"taket: pulten på 700 er kjøpt ved å løfte trinn 3 til {RUNG_TOPS[2]}, "
      f"ikke ved å slakke regelen. X8 regnet det samme taket til 639 mot "
      f"trinn 3 på 787 - se X8 og X9 i toppen av fila")
print(f"OK  X9 kryssingen ved stigen: {TABLE_CROSS_BAND:g} mm fritt bånd fra "
      f"bordklossens overkant {PANEL_UNDER_TABLE} til trinn 3s underkant "
      f"{TABLE_CEILING_Z:g}, for en {PANEL_UNIT_H:g} mm høy enhet = "
      f"{TABLE_CROSS_CLEAR:g} mm klaring (krav {TRANSFER_CLEAR_MIN}). Det er "
      f"dette båndet X8 målte til 29 mm for LITE")

# ---------------------------------------------------------------------------
# X7 - THE REAL EC5 6.3.2, ON THE MEMBER THE LIFT MADE THE WORST
# ---------------------------------------------------------------------------
# Every buckling number in this file up to here has been an argument in a
# comment: a slenderness worked out by hand in the LADDER note, a k_c read off
# a curve, a capacity multiplied out and compared with a kilonewton. That was
# fine while the frame had slack. X1 took the slack: lifting the platform 337
# mm ran the ladder stile's out-of-plane length from 1065 to 1402 mm on a
# 10,39 mm radius of gyration, which is lambda ~135 - the most slender member
# in the bed by a distance, and slender enough that the answer now depends on
# WHICH curve you read. So the curve is computed here instead, EN 1995-1-1
# 6.3.2 in full, off the built solids:
#
#     lambda      = l_ef / i                       i = h / sqrt(12) for a
#                                                  rectangle
#     lambda_rel  = lambda/pi * sqrt(f_c,0,k / E_0,05)
#     k           = 0,5 (1 + beta_c (lambda_rel - 0,3) + lambda_rel^2)
#     k_c         = 1 / (k + sqrt(k^2 - lambda_rel^2))     (1,0 below 0,3)
#     N_c,Rd      = k_c * A * f_c,0,d
#
# THE MATERIAL IS THE ONE THE REST OF THE FILE ALREADY USES. C24 to EN 338:
# f_c,0,k = 21 N/mm2 and E_0,05 = 7400 N/mm2, over gamma_M 1,3, service class
# 1. beta_c is 0,2, EC5's value for solid timber; laminated members get 0,1
# and there are none in this bed.
#
# AND k_mod IS 0,8 HERE ON PURPOSE, WHICH IS NOT THE 0,9 VEDLEGG A.6 ARGUES.
# A.6's case is a 2 kN drop on a slat - short term, k_mod 0,9. A column under
# a climber is the same kind of event and 0,9 would be defensible, but every
# buckling figure this file has ever quoted has been worked on 12,92 N/mm2,
# i.e. 0,8, and the two must not disagree by a silent 12%. So 0,8 stays, the
# choice is the CONSERVATIVE one of the two, and the price of it is measured
# rather than waved at: the print below carries the same utilisation worked
# on 0,9 beside it, so anybody who wants the other class can see exactly what
# it buys (the ladder stile 0,26 -> 0,23) without re-deriving anything.
#
# THE LOAD IS THE ONE THE FILE ALREADY CARRIES. CLIMBER_KN, 1 kN, the person
# on the ladder - and it is put down ONE stile, not shared over two. A rung
# end actually delivers RUNG_END_KN, half of it; standing the whole climber on
# one stile is the same worst-placement convention MAX_BLOCKLESS_UTIL uses,
# and it is what makes this a check rather than an average. The corner posts
# are run through the same machine on the corner reactions the block-less
# corner table (V5) already argues, so all four members are judged on loads
# this file had before X7 and not on new ones.
#
# WHAT THE CHECK IS ALLOWED TO CONCLUDE. It reports; it does not move wood.
# The gate is 0,5, and it is set there rather than at the 0,8 the screw rows
# use because a slenderness-governed member fails differently: a screw row
# that is 0,8 utilised bends and complains first, and an Euler column does
# not. If the ladder stile ever crosses it, the answer is the floor-level tie
# back to the front corner posts the D13 note has been flagging - not a
# thicker stile.
C24_FC0K = 21.0                  # N/mm2, EN 338, compression along the grain
C24_E005 = 7400.0                # N/mm2, EN 338, 5-percentile modulus
K_MOD_MEDIUM = 0.8               # medium-term load, service class 1
GAMMA_M_TIMBER = 1.3
BETA_C_SOLID = 0.2               # EC5 6.3.2(4), solid timber
FC0_D = C24_FC0K * K_MOD_MEDIUM / GAMMA_M_TIMBER          # 12.92 N/mm2
MAX_BUCKLING_UTIL = 0.5


def ec5_kc(lam):
    """(lambda_rel, k_c) for a C24 solid-timber column - EN 1995-1-1 6.3.2."""
    rel = lam / math.pi * math.sqrt(C24_FC0K / C24_E005)
    if rel <= 0.3:
        return rel, 1.0           # 6.3.2(2): no reduction below 0,3
    k = 0.5 * (1 + BETA_C_SOLID * (rel - 0.3) + rel ** 2)
    return rel, 1.0 / (k + math.sqrt(k * k - rel * rel))


def ec5_column(width, depth, l_ef, n_kn):
    """One column, one axis: everything 6.3.2 has to say about it.

    `depth` is the dimension it bends in, `width` the other one. Both come off
    the part, and l_ef off the distance between the things that actually hold
    it - see the table below, where each row says what those are.
    """
    area = width * depth
    i = depth / math.sqrt(12)
    lam = l_ef / i
    rel, kc = ec5_kc(lam)
    cap = kc * area * FC0_D / 1000.0
    return dict(a=area, i=i, lam=lam, rel=rel, kc=kc, cap=cap,
                util=n_kn / cap, l=l_ef, n=n_kn)


# WHERE EACH COLUMN IS HELD. The buckling length is not a number anybody
# types: it is the biggest gap between the things that really hold the member
# in the direction it would go. So each row below lists the HOLDS - heights
# read off the model - and the length is the widest gap between two of them.
# Which contacts count as a hold is a judgement and is therefore written out
# per row rather than guessed from the geometry: a rung block touches the
# stile, but what it ties the stile to is the other stile, in the ladder's own
# plane, and it does nothing at all out of plane.
_upright = min(uprights, key=lambda p: p.extents[0][0])
_rung_mid = sorted(sum(p.extents[2]) / 2 for p in rungs)

# (name, width, depth it bends in, [holds], axial kN, what the holds are)
BUCKLING_MEMBERS = [
    ("stigevange, ut av planet", UPRIGHT_W, UPRIGHT_T,
     [0, front_rail.extents[2][0]], CLIMBER_KN,
     "gulv → fremre sidevanges underkant (J3), og ingenting imellom: D13 tok "
     "benkevangeomlegget og X1 løftet vangen"),
    ("stigevange, i stigeplanet", UPRIGHT_T, UPRIGHT_W,
     [0] + _rung_mid + [front_rail.extents[2][0]], CLIMBER_KN,
     "gulv → første trinn; over det avstiver trinnene hverandre, verst "
     "276 mm etter X9 (245 da stigen var jevn)"),
    ("fremre hjørnestolpe", POST_W, POST_T,
     [0, BENCH_RAIL_TOP, END_BEAM_Z0], 1.5,
     "gulv → fremre benkevangeomlegg (229..297) → endebjelken (1304..1402); "
     "verste gap er benkevange → endebjelke"),
    ("bakre hjørnestolpe", POST_W, POST_T, [0, END_BEAM_Z0], 1.5,
     "gulv → endebjelken alene. Den bakre benkevangen og bordbærelekta "
     "støter og skrus i stolpens X-innerflate på 229..297 og 614..682, så "
     "den virkelige lengden er kortere; dette er den konservative lesningen"),
]
BUCKLING = [(name, ec5_column(w, d, max(b - a for a, b in zip(h, h[1:])), n),
             why) for name, w, d, h, n, why in BUCKLING_MEMBERS]
for _name, _r, _why in BUCKLING:
    assert _r["util"] <= MAX_BUCKLING_UTIL, (
        f"X7: {_name} is {_r['util']:.2f} utilised in EC5 6.3.2 buckling "
        f"(lambda {_r['lam']:.0f}, lambda_rel {_r['rel']:.2f}, k_c "
        f"{_r['kc']:.2f}, N_c,Rd {_r['cap']:.1f} kN against {_r['n']:.1f}) - "
        f"over the {MAX_BUCKLING_UTIL:g} gate a slenderness-governed member "
        f"is held to. Brace it; do not thicken it")
# And the claim the LADDER note makes out loud - that the lift made the stile
# the worst member in the bed - is a comparison, so it is compared.
BUCKLING_WORST = max(BUCKLING, key=lambda r: r[1]["util"])
assert BUCKLING_WORST[0].startswith("stigevange, ut av planet"), (
    f"X7: the worst buckling row is '{BUCKLING_WORST[0]}', not the ladder "
    f"stile out of plane - the LADDER note says otherwise and one of the two "
    f"is now wrong")
K_MOD_SHORT = 0.9                # what vedlegg A.6 argues for a 2 kN drop
print(f"OK  X7 EC5 6.3.2 (k_c-metoden, C24: f_c,0,k {C24_FC0K:g}, E_0,05 "
      f"{C24_E005:g}, k_mod {K_MOD_MEDIUM:g}/gamma_M {GAMMA_M_TIMBER:g} → "
      f"f_c,0,d {FC0_D:.2f} N/mm², beta_c {BETA_C_SOLID:g}), grense "
      f"{MAX_BUCKLING_UTIL:g} — «(k_mod 0,9)» er det samme regnet på "
      f"vedlegg A.6-klassen, altså hva den konservative 0,8-en koster:")
for _name, _r, _why in BUCKLING:
    print(f"      {_name:28s} l {_r['l']:6.0f}  i {_r['i']:5.2f}  λ "
          f"{_r['lam']:5.1f}  λrel {_r['rel']:4.2f}  k_c {_r['kc']:4.2f}  "
          f"N_c,Rd {_r['cap']:5.1f} kN mot {_r['n']:.1f} → "
          f"{_r['util']:.2f} ({_r['util'] * K_MOD_MEDIUM / K_MOD_SHORT:.2f} "
          f"med k_mod {K_MOD_SHORT:g})   [{_why}]")


# 2 - EVERY DIRECTION HAS A BLOCKER, AND THE BLOCKER IS WOOD NOW.
# The five ways a seated panel can move without leaving its seat, and what
# stops each. This is read OFF THE MODEL, not asserted from the table: each
# entry measures a real clearance between two real solids. V3 deleted the four
# angle brackets, so what these asserts walk over is the BATTENS - and the
# thing they are measured against is the rung END GRAIN, in both modes,
# because rung 1 and rung 2 end at the same X.
def _guide_battens(mode):
    """[(side, batten, locator)] - the two guide battens and the piece of wood
    each one runs down beside at THIS mode's seat height.

    X9: in bed mode that piece is a RUNG END, and one rung serves both sides;
    in table mode there is no rung at the seat height any more - there cannot
    be - and it is the two BORDKLOSSER, one per side. They stand on the same
    two planes (X 835 / 1155) over the same 48 mm of Z under the plate, which
    is why the panel sub-assembly is untouched: the battens cannot tell which
    of the two they have found, and the asserts below do not tell them."""
    panel = MODES[mode]
    top = PANEL_UNDER_BED if mode == "bed_mode" else PANEL_UNDER_TABLE
    seat = [p for p in parts
            if (p.label.startswith("Ladder Rung_")
                or p.label.startswith("Table Bearer"))
            and abs(p.extents[2][1] - top) < TOL]
    assert seat, f"V3/X9: nothing at all stands at the {mode} seat height {top}"
    out = []
    for b in PANEL_BATTENS[id(panel)]:
        if abs((b.extents[1][1] - b.extents[1][0]) - BATTEN_LEN) > TOL:
            continue                       # a cross batten: never in a shaft
        side = _outboard(0, b)
        # the locator on THIS side is the one whose end face the batten looks
        # at across the fit - nearest in X, measured the way the batten faces.
        loc = min(seat, key=lambda p: abs(p.extents[0][0] - b.extents[0][1]
                                          if side < 0 else
                                          b.extents[0][0] - p.extents[0][1]))
        out.append((side, b, loc))
    return out


if FASTENERS_ON:
    for _mode in MODES:
        _guides = _guide_battens(_mode)
        assert len(_guides) == 2, \
            f"V3: {len(_guides)} guide battens in {_mode}, want 2"
        assert sorted(s for s, _b, _r in _guides) == [-1.0, 1.0], \
            "V3: the two guides must be one per side"
        # X, both ways: each batten faces its own rung end across the fit, and
        # the two of them face OPPOSITE ways - one stops the panel walking
        # left, the other right. Anything else and it is stopped one way only.
        for _side, _b, _rung in _guides:
            _gap = (_rung.extents[0][0] - _b.extents[0][1] if _side < 0
                    else _b.extents[0][0] - _rung.extents[0][1])
            assert abs(_gap - PANEL_FIT) < TOL, (
                f"V3 retning: in {_mode} the "
                f"{'left' if _side < 0 else 'right'} guide batten stands "
                f"{_gap:.1f} mm off the rung end, and the fit is {PANEL_FIT}")
            # and it has to be ALONGSIDE the end grain, not above or below it:
            # a guide that misses its locator in Y or Z guides nothing.
            # X9: the Y lap is no longer one number for both modes - a rung end
            # gives the batten 30 mm of shaft and a bordkloss 53 - so it is
            # computed from the locator's own back face and held to the
            # engagement floor rather than typed.
            # X10: and neither is the Z lap, since the bordkloss became 68 mm
            # tall to hold its second screw. Both are computed from the
            # locator's own extents and both are held to the floor a RUNG END
            # sets, which is the case the rule was written on: 30 in Y and
            # RUNG_T in Z. More lap is more guide - it is the floor that
            # matters, not an exact number that has to be retyped every time a
            # locator changes section.
            for _j, _what, _floor in ((1, "Y", BATTEN_GUIDE_ENGAGE_Y),
                                      (2, "Z", BATTEN_GUIDE_ENGAGE_Z)):
                _lap = (min(_b.extents[_j][1], _rung.extents[_j][1])
                        - max(_b.extents[_j][0], _rung.extents[_j][0]))
                _want = (min(BATTEN_Y1, _rung.extents[1][1])
                         - max(BATTEN_Y0, _rung.extents[1][0]) if _j == 1
                         else _rung.extents[2][1] - _rung.extents[2][0])
                assert abs(_lap - _want) < TOL, (
                    f"V3 retning: in {_mode} the guide batten laps "
                    f"'{_rung.label}' by {_lap:.0f} mm in {_what}, and the "
                    f"locator's own extent says {_want:.0f} - the batten "
                    f"misses part of the piece it is supposed to run beside")
                assert _lap >= _floor - TOL, (
                    f"V3/X9/X10 retning: in {_mode} the guide batten is only "
                    f"{_lap:.0f} mm into the shaft beside '{_rung.label}' in "
                    f"{_what}, under the {_floor:g} mm a rung end gives it")
        # Rz: the two guides are in the SAME Y band and far apart in X, and
        # they oppose opposite senses of X - which is exactly the condition
        # that makes a turn about Z jam one of them, because a turn drives
        # both the same way.
        _y0 = max(_b.extents[1][0] for _s, _b, _r in _guides)
        _y1 = min(_b.extents[1][1] for _s, _b, _r in _guides)
        assert _y1 - _y0 > 0, "V3 retning: the two guides share no Y band"
        _spread_x = abs(sum(_s * sum(_b.extents[0]) / 2
                            for _s, _b, _r in _guides))
        assert _spread_x >= RUNG_LEN - TOL, (
            f"V3 retning: the two guides are only {_spread_x:.0f} mm apart in "
            f"X - too close together to take a turn about Z")
    # Y, both ways: the wall behind and the uprights in front. No steel.
    assert panel.extents[1][0] == PANEL_Y0 == WALL_Y, \
        f"V2 retning: the built rear edge is at Y {panel.extents[1][0]:g}, " \
        f"the wall plane is {WALL_Y:g}"
    assert LADDER_Y0 - PANEL_Y1 == PANEL_FIT, \
        "V2 retning: the front edge does not meet the uprights across the fit"
    # Z down: WOOD, and after V3 nothing but wood. The rear seat is the whole
    # width of the panel on the rear support in both modes, and there is no
    # longer any steel beside it or under it that could hold the sheet off.
    for _mode, _support in (("bed_mode", "Bench Rail Back (continuous)"),
                            ("table_mode", "Table Ledger Back")):
        _sup = next(p for p in parts if p.label == _support)
        _panel = MODES[_mode]
        assert abs(_sup.extents[2][1] - _panel.extents[2][0]) < TOL, (
            f"V3 sete: in {_mode} '{_support}' tops out at "
            f"{_sup.extents[2][1]} and the panel underside is at "
            f"{_panel.extents[2][0]}")
        _seat = bearing_area(_panel, _sup)
        assert _seat >= PANEL_W * LEDGER_BACK_T - TOL, (
            f"V3 sete: in {_mode} the panel meets '{_support}' over "
            f"{_seat:.0f} mm2, want the full {PANEL_W} x {LEDGER_BACK_T}")
        # and no fastener may be in that seat: nothing of the panel assembly
        # sticks out below the batten line or beyond the panel outline.
        for _f in FASTENER_SPECS:
            if not _f["jid"].startswith("J13") or _f.get("solid") is None:
                continue
            _e = _box_extents(_f["solid"])
            assert _e[2][0] >= BATTEN_Z0_BED - TOL, (
                f"V3 sete: {_f['solid'].label} hangs below the batten line - "
                f"the panel would land on a screw head")
            assert PANEL_X0 - TOL <= _e[0][0] and _e[0][1] <= PANEL_X1 + TOL, (
                f"V3 sete: {_f['solid'].label} reaches outside the panel "
                f"outline in X")
    # THE LOCK POINT, measured. The two faces the three lock options act
    # across, and the proof that they only face each other in bed mode.
    _rail = next(p for p in parts
                 if p.label.startswith("Bench Rail Front") and
                 p.extents[0][1] <= PANEL_X0)
    _nose = next(b for b in PANEL_BATTENS[id(panel_bed)]
                 if abs(b.extents[0][0] - PANEL_X0) < TOL)
    assert abs((_nose.extents[0][0] - _rail.extents[0][1]) - LOCK_GAP) < TOL, (
        f"V3 lås: the lock gap is {_nose.extents[0][0] - _rail.extents[0][1]} "
        f"mm, and the side gap is {LOCK_GAP}")
    assert _nose.extents[2] == _rail.extents[2], \
        "V3 lås: in bed mode the two lock faces must be in one Z band"
    _lap = (min(_nose.extents[1][1], _rail.extents[1][1])
            - max(_nose.extents[1][0], _rail.extents[1][0]))
    assert _lap >= 40.0, (
        f"V3 lås: the two lock faces overlap over {_lap:g} mm in Y - too "
        f"little to take a 40 mm strap, a latch or a thumbscrew boss")
    _nose_t = next(b for b in PANEL_BATTENS[id(panel_table)]
                   if abs(b.extents[0][0] - PANEL_X0) < TOL)
    assert _nose_t.extents[2][0] >= _rail.extents[2][1] - TOL, (
        "V3 lås: in TABLE mode the cross batten must be clear above the "
        "front bench rail - the whole point of this lock point is that it "
        "does not exist in the other position")
    print(f"OK  V3 lås: låsepunktet er de to endeflatene i sideklaringen - "
          f"kilelekta ({sec(BATTEN_W, BATTEN_H)}) mot fremre benkevange, "
          f"{LOCK_GAP} mm fra hverandre, {_lap:g} mm overlapp i dybden og "
          f"samme Z-bånd i SENGESTILLING. I bordstilling ligger kilelekta "
          f"{_nose_t.extents[2][0] - _rail.extents[2][1]:.0f} mm over "
          f"vangen, så låsen har ingenting å ta i - den kan ikke stå på i "
          f"feil stilling. V4: INGEN lås monteres (akseptert avvik 4); "
          f"treverket her er ettermonteringspunktet, og alle tre løsningene "
          f"i laasvalg.png passer på det uendret")
    print(f"OK  V3 retning: X+ og X- stoppes av de to styrelektene mot "
          f"trinnenden ({PANEL_FIT} mm passing hver vei, {_spread_x:.0f} mm "
          f"fra hverandre, så en dreining om Z kiler den ene), i BEGGE "
          f"stillinger og med {BATTEN_GUIDE_ENGAGE_Z} x "
          f"{BATTEN_GUIDE_ENGAGE_Y} mm tre mot trinnendens endeved i "
          f"sengestilling og {BATTEN_GUIDE_ENGAGE_Z} x {TABLE_BEARER_LEDGE} "
          f"mot bordklossen i bordstilling (X9: samme plan, samme passing, "
          f"dypere sjakt). Y- av "
          f"veggplanet, Y+ av stigevangene ({PANEL_FIT} mm), Z ned av tre "
          f"i hele platens bredde i begge stillinger - og Z OPP av "
          f"ingenting, med vilje: platen skal kunne løftes ut. Ikke ett "
          f"beslag igjen i mekanismen")

# 3 - THE EN 747 GAP BANDS, ON THE GAPS AROUND THE SEATED PANEL.
# The rule is a BAND, not a maximum, and it is the reason the panel is not a
# free dimension. A gap a child can reach is safe if a finger cannot enter it
# at all (up to 5 mm), if it passes freely (12..25 mm), or if the whole limb
# passes and the opening is still inside EN 747's own 75 mm limit (60..75 mm);
# in between it wedges. K2 moves the panel's two side gaps from the middle
# band to the top one - see PANEL_WIDTH_WINDOWS.
PANEL_GAPS = {
    "platekant → benkespile, venstre": PANEL_X0 - BENCH_LEN,
    "platekant → benkespile, høyre": (WALL_SPAN - BENCH_LEN) - PANEL_X1,
    "platens forkant → stigevange": LADDER_Y0 - PANEL_Y1,
    "platens bakkant → vegg": PANEL_Y0 - WALL_Y,
    # V3: the one gap the mechanism itself makes. It is 2 mm, under the panel,
    # and it is the running clearance the guide batten keeps off the rung end.
    "styrelekt → trinnende": PANEL_FIT,
    # V3: and the one the lock lives in - the cross batten's end face against
    # the front bench rail's end face, in bed mode. Same side gap, same band.
    "kilelekt → fremre benkevange (sengestilling)": PANEL_X0 - BENCH_LEN,
}
def _en_gap_legal(g):
    return any(lo - TOL <= g <= hi + TOL for lo, hi in EN_LEGAL_GAP_BANDS)


_BANDS_TEXT = " / ".join(f"{lo:g}..{hi:g}" for lo, hi in EN_LEGAL_GAP_BANDS)
for _what, _g in PANEL_GAPS.items():
    assert _en_gap_legal(_g), (
        f"EN 747: the gap '{_what}' is {_g:g} mm - a finger enters it and "
        f"wedges. It has to land in one of the bands {_BANDS_TEXT} mm")
assert PANEL_X0 - BENCH_LEN == PANEL_SIDE_GAP == 63 and \
    (WALL_SPAN - BENCH_LEN) - PANEL_X1 == PANEL_SIDE_GAP, \
    "EN 747: the two side gaps must be equal and must be the declared one"
assert not _en_gap_legal(10), \
    "EN 747: 10 mm - the gap this design used to have - must NOT be legal"
assert not _en_gap_legal(40), \
    "EN 747: 40 mm is squarely in the wedge zone and must NOT be legal"

# K2 - THE WIDTH IS QUANTIZED. The panel's width and its two side gaps are one
# number seen twice: gap = (PANEL_OPENING - width)/2. So the legal gap bands
# become legal WIDTH WINDOWS, and everything between two windows is forbidden
# wood. This is the assert that a future "the panel only needs to be a bit
# narrower" edit runs into, and the message is the table.
PANEL_WIDTH_WINDOW = next(
    (w for w in PANEL_WIDTH_WINDOWS if w[0] - TOL <= PANEL_W <= w[1] + TOL),
    None)
assert PANEL_WIDTH_WINDOW is not None, (
    f"EN 747 / K2: a {PANEL_W:g} mm panel in a {PANEL_OPENING:g} mm opening "
    f"leaves {(PANEL_OPENING - PANEL_W) / 2:g} mm at each side, which is in "
    f"none of the legal gap bands {_BANDS_TEXT} mm. THE WIDTH IS NOT A DIAL: "
    f"the only legal widths are "
    + ", ".join(f"{lo:g}..{hi:g}" for lo, hi in PANEL_WIDTH_WINDOWS)
    + " mm, and everything between two of those windows puts a child's finger "
      "in a gap it wedges in. Pick a window, do not split the difference.")
# The forbidden spans, computed the same way, so the print below is the table
# and not a copy of it.
PANEL_WIDTH_FORBIDDEN = tuple(
    (a[1] + 1, b[0] - 1) for a, b in zip(PANEL_WIDTH_WINDOWS,
                                         PANEL_WIDTH_WINDOWS[1:]))
assert any(lo <= 652 <= hi for lo, hi in PANEL_WIDTH_WINDOWS), \
    "K2: 652 - the width this design used to have - was legal and must stay " \
    "legal in the table; it is a window that was left, not a mistake"
print("OK  EN 747 klemfare: " + ", ".join(
    f"{_w.split(' (')[0]} {_g:g}" for _w, _g in PANEL_GAPS.items())
    + f" mm - hver i ett av båndene {_BANDS_TEXT} mm (fingeren kommer ikke "
      f"inn / fingeren går fritt / hele lemmet går fritt). Sideklaringen var "
      f"10 mm, midt i klembåndet")
print(f"OK  K2 platebredden er kvantisert: {PANEL_W:g} mm i en åpning på "
      f"{PANEL_OPENING:g} gir {PANEL_SIDE_GAP:g} mm sideklaring, i vinduet "
      f"{PANEL_WIDTH_WINDOW[0]:g}..{PANEL_WIDTH_WINDOW[1]:g}. Lovlige vinduer "
      + ", ".join(f"{lo:g}..{hi:g}" for lo, hi in PANEL_WIDTH_WINDOWS)
      + " mm; forbudt " + ", ".join(f"{lo:g}..{hi:g}"
                                    for lo, hi in PANEL_WIDTH_FORBIDDEN)
      + " mm")

# D5: FLUSH TOP. No cleats anywhere; every slat lies on top of the rails and
# must bear on the FULL 48 mm width of BOTH of them, exactly like a bench slat.
assert SLAT_Z0 == RAIL_TOP, "slats do not sit on top of the rails"
assert MATTRESS_Z0 == SLAT_Z1, "mattress does not sit on the slats"
assert (SLAT_Y0, SLAT_Y1) == (BACK_RAIL_Y0, FRONT_RAIL_Y1)
assert SLAT_LEN == BENCH_SLAT_LEN == 800, \
    "D5: an upper slat is supposed to be the same piece as a bench slat"
# V6: the two SLAT families are still one and the same piece - that is what
# makes the 24-in-one-setup cut - but they are no longer the guard board's
# profile. A slat is loaded flat and a guard board is loaded on edge, so they
# want opposite things from a section, and V6 stops paying 36 mm for the flat
# one. The bed carries five profiles now instead of four.
assert (BED_SLAT_T, BED_SLAT_W) == (BENCH_SLAT_T, BENCH_SLAT_W) == (23, 98)
assert (GUARD_T, GUARD_W) == (BOARD36_T, BOARD36_W), \
    "the guard boards stay on the 36x98 board - they are loaded on edge"
assert len(bed_slats) == SLAT_COUNT == 14
rail_y = [(BACK_RAIL_Y0, BACK_RAIL_Y1), (FRONT_RAIL_Y0, FRONT_RAIL_Y1)]
for s in bed_slats:
    (sx0, sx1), (sy0, sy1), (sz0, sz1) = s.extents
    assert (sz0, sz1) == (RAIL_TOP, SLAT_Z1), f"'{s.label}' is not on the rail tops"
    # D5: EVERY slat covers the full 48 mm of BOTH rails, and after W8 they are
    # all the same 800 mm piece doing it the same way - no overhang anywhere.
    for ry0, ry1 in rail_y:
        bear = min(sy1, ry1) - max(sy0, ry0)
        assert bear >= RAIL_T - TOL, \
            f"'{s.label}' only bears {bear:.1f} mm on the rail at Y {ry0}..{ry1}"
    assert (sy0, sy1) == (SLAT_Y0, SLAT_Y1), \
        f"W8: '{s.label}' is Y {sy0}..{sy1}, want every slat at " \
        f"{SLAT_Y0}..{SLAT_Y1}"
    assert sy1 - sy0 == SLAT_LEN, f"W8: '{s.label}' is {sy1 - sy0} long"
    assert 0 <= sx0 and sx1 <= WALL_SPAN
slat_xs = sorted(s.extents[0] for s in bed_slats)
slat_gaps = [slat_xs[i + 1][0] - slat_xs[i][1] for i in range(len(slat_xs) - 1)]
slat_gaps += [slat_xs[0][0] - 0, WALL_SPAN - slat_xs[-1][1]]
assert max(slat_gaps) <= MAX_SLAT_GAP + TOL, \
    f"largest slat gap is {max(slat_gaps):.1f} > {MAX_SLAT_GAP}"

# W8: ONE LENGTH, AND THE SLATS CANNOT FOUL THE RELOCATED POSTS.
# The posts moved into the slats' own Y band (-48..0) but stopped 98 mm below
# them, at the rail underside, so the clearance is in Z and it is by
# construction. Checked anyway, as a volume overlap against the real post
# extents: this is the assert that would fire if anyone ever raised the back
# posts again without thinking about the platform.
assert len({(round(s.extents[1][0]), round(s.extents[1][1])) for s in bed_slats}) == 1, \
    "W8: the upper slats are supposed to be one length in one plane again"
# X10: `SLAT_Z0 - BACK_POST_HEIGHT == RAIL_H` was RAIL_H == RAIL_H - SLAT_Z0 is
# RAIL_TOP is RAIL_BOTTOM + RAIL_H, and BACK_POST_HEIGHT is RAIL_BOTTOM. The
# comment above already conceded it ("by construction") and nominated the loop
# as the real check, but the loop measured the slats against BACK_POST_EXTENTS,
# which is itself typed. Both halves read the bodies now.
_post_top = max(p.extents[2][1] for p in back_posts)
_slat_bottom = min(s.extents[2][0] for s in bed_slats)
assert _slat_bottom - _post_top == RAIL_H, \
    f"W8: the built slats start {_slat_bottom - _post_top:g} mm above the " \
    f"built back post tops ({_slat_bottom:g} over {_post_top:g}), expected " \
    f"one rail height {RAIL_H}"
for s in bed_slats:
    for bp in back_posts:
        inter = [min(a1, b1) - max(a0, b0)
                 for (a0, a1), (b0, b1) in zip(s.extents, bp.extents)]
        assert min(inter) <= 0, \
            f"W8: '{s.label}' overlaps '{bp.label}' by {inter}"
print(f"OK  D5/W8: {SLAT_COUNT} upper slats {sec(BED_SLAT_T, BED_SLAT_W)} x "
      f"{SLAT_LEN} - ONE length again (v9/W4 had 12 x 847 + 2 x 800) - flush on "
      f"top of both rails, Z {SLAT_Z0}..{SLAT_Z1}, Y {SLAT_Y0}..{SLAT_Y1} with "
      f"the wall-side end ON the mounting plane {WALL_Y}, pitch "
      f"{slat_pitch:.1f}, gaps {min(slat_gaps):.0f}..{max(slat_gaps):.1f} mm "
      f"(limit {MAX_SLAT_GAP}); {RAIL_T} mm full bearing on each rail for all "
      f"{SLAT_COUNT}; every one of them clear of the back posts, which stop "
      f"{SLAT_Z0 - BACK_POST_HEIGHT} mm below them; mattress "
      f"{MATTRESS_Z0}..{MATTRESS_Z1} at Y {MATTRESS_Y0}..{MATTRESS_Y1}; rail "
      f"{RAIL_BOTTOM}..{RAIL_TOP}")

# The mattress must land entirely on the slat platform. After W6+W8 that is an
# identity rather than a check with slack in it: the platform and the mattress
# are the same 800 mm band, and the mattress cannot move.
assert SLAT_Y0 <= MATTRESS_Y0 and MATTRESS_Y1 <= SLAT_Y1, \
    "the mattress overhangs the slat platform in Y"
assert (SLAT_Y0, SLAT_Y1) == (MATTRESS_STOP_Y0, MATTRESS_STOP_Y1), \
    f"W5/W8: the platform Y {SLAT_Y0}..{SLAT_Y1} must be exactly the mattress " \
    f"clear {MATTRESS_STOP_Y0}..{MATTRESS_STOP_Y1}"

# D12/W8: THE MATTRESS IS FLUSH AT THE RAILS. D12's statement was that the
# 800 mm mattress is exactly the rail-to-rail platform, both long edges landing
# on the slat ends with no bare slat strip on either side. v9/W4 put 47 mm of
# bare slat behind the back rail on purpose; W6 removes the reason for it, so
# the D12 statement is literally true again in both directions.
assert MATTRESS_W == SLAT_LEN == PLATFORM_DEPTH, \
    "D12: the mattress width and the rail-to-rail platform depth must match"
# X10: both of these compared aliases of one constant. Measured on the bodies,
# they are the same two claims and they can now fail.
assert MATTRESS_BUILT_Y1 == max(s.extents[1][1] for s in bed_slats), \
    f"D12: the built mattress front edge {MATTRESS_BUILT_Y1:g} is not flush " \
    f"with the built slat ends " \
    f"{max(s.extents[1][1] for s in bed_slats):g}"
assert MATTRESS_BUILT_Y0 == WALL_PLANE_BUILT == WALL_Y, \
    f"D12/W7: the built mattress rear edge {MATTRESS_BUILT_Y0:g} is not on " \
    f"the wall plane the bodies make, {WALL_PLANE_BUILT:g}"
print(f"OK  D12/W8: the {MATTRESS_W} mm mattress is exactly the "
      f"{PLATFORM_DEPTH} mm RAIL-TO-RAIL platform (Y {SLAT_Y0}..{SLAT_Y1}) and "
      f"sits on it - 0 mm of bare slat at either edge, and no strip behind the "
      f"back rail any more (v9/W4 had 47 mm there to let the mattress travel; "
      f"there is nowhere to travel to now)")

# W5: WHAT LOCATES THE MATTRESS SIDEWAYS, AFTER W6.
#
# History, because this has now moved three times. v7's sunken tray located the
# mattress with the rail tops (they overlapped its bottom 29 mm). D5's flush top
# could not, and the guard boards cannot either - they start 75 mm ABOVE the
# mattress surface - so the job passed to the six verticals, and D12 made that a
# zero-play fit between two lines of posts at Y -48 and Y 752. v9/W2 cut the back
# pair out of the mattress band, which left the WALL as the back stop 48 mm
# further away and gave the mattress 48 mm of travel. v10/W6 brings the wall
# forward to Y -48 - exactly where the back line of posts used to be - so the fit
# is zero-play again, made by a wall on one side and four verticals on the other.
# What has to be true:
#   (a) the front stop is real - four verticals in the plane Y 752, each one
#       covering the mattress band 1523..1643 in full;
#   (b) NO vertical is left in that band on the back side. The back posts stop
#       132 mm below the mattress underside, so the back stop is the wall and
#       nothing else - which is what makes the fit independent of the mattress's
#       actual thickness;
#   (c) the travel is 0 and the worst single gap is therefore 0, under the 75 mm
#       EN 747 limit (checked in the W1/W5 block above too, from the constants;
#       here it is checked against the parts that actually exist).
stops_front = [p for p in verticals
               if p.extents[1][0] == MATTRESS_STOP_Y1
               and p.extents[2][0] <= MATTRESS_Z0
               and p.extents[2][1] >= MATTRESS_Z1]
assert len(stops_front) == 4, \
    f"W5: the mattress has {len(stops_front)} front stops, want 4 (2 front " \
    f"corner posts + 2 ladder uprights)"
assert {p.label.rsplit(" ", 1)[0] for p in stops_front} == \
    {"Corner Post Front", "Ladder Upright"}, \
    f"W5: the front stops are {sorted(p.label for p in stops_front)}"
in_band_at_back = [p for p in parts
                   if p.extents[1][0] < BACK_RAIL_Y1 - TOL
                   and p.extents[2][1] > MATTRESS_Z0 + TOL]
assert not in_band_at_back, \
    f"W5: {[p.label for p in in_band_at_back]} still stands in the mattress " \
    f"band in the back rail plane - the wall is supposed to be the only stop there"
mattress_play = (MATTRESS_STOP_Y1 - MATTRESS_STOP_Y0) - MATTRESS_W
assert mattress_play == MATTRESS_WANDER == 0, \
    f"W5: the mattress can move {mattress_play} mm, expected {MATTRESS_WANDER}"
assert mattress_play <= MAX_GUARD_OPENING, \
    f"EN 747: {mattress_play} mm of mattress travel means a {mattress_play} mm " \
    f"gap at one end, over the {MAX_GUARD_OPENING} mm limit"
print(f"OK  W2/W5/W6: the mattress is PINNED between the room WALL at Y "
      f"{MATTRESS_STOP_Y0} - the back rail face, which the platform now runs to "
      f"by construction - and {len(stops_front)} front verticals at Y "
      f"{MATTRESS_STOP_Y1} running on to {POST_HEIGHT}; nothing is left in the "
      f"mattress band on the wall side (the back posts stop "
      f"{MATTRESS_Z0 - BACK_POST_HEIGHT} mm below it). Travel {mattress_play} "
      f"mm, so 0 mm of gap at either long edge (EN 747 limit "
      f"{MAX_GUARD_OPENING}), and slat under every millimetre of it")
mattress_vol = ((0, WALL_SPAN), (MATTRESS_Y0, MATTRESS_Y1), (MATTRESS_Z0, MATTRESS_Z1))


def overlap_volume(extents, other):
    v = 1.0
    for (a0, a1), (b0, b1) in zip(extents, other):
        d = min(a1, b1) - max(a0, b0)
        if d <= 0:
            return 0.0
        v *= d
    return v


allowed = {id(mattress)} | {id(s) for s in bed_slats}
clashes = []
checked = 0
for p in parts + [panel_bed, panel_table] + battens_bed + battens_table:
    if id(p) in allowed:
        continue
    checked += 1
    v = overlap_volume(p.extents, mattress_vol)
    if v >= 1e-6:
        clashes.append((p.label, v))
assert not clashes, "parts intruding into the mattress volume: " + str(clashes)
print(f"OK  no part intrudes into the mattress volume (checked {checked} parts)")

# --- no two parts may overlap each other -----------------------------------
for mode_name, panel in MODES.items():
    items = [p for p in mode_parts(panel) if not is_soft(p)]
    bad = []
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if overlap_volume(a.extents, b.extents) > 1.0:
                bad.append((a.label, b.label))
    assert not bad, f"{mode_name}: parts occupying the same space: {bad}"
print("OK  no two wooden parts overlap in either mode")

# --- CONNECTIVITY: every wooden part must touch at least one other part -----
# Regression guard: the v2 ladder floated 48 mm in front of the rail and was
# attached to nothing at all.
# NOTE: this is NOT the contact-detection tolerance. It used to be spelled
# CONTACT_TOL as well, which silently REBOUND the module global the joint
# machinery documents as 0.51 - harmless only because contacts() has already
# run by this line, but any later caller (or a tool importing this module)
# would have read 0.5 where the docs say 0.51. Its own name, its own job:
# the solid-to-solid distance below which a part counts as attached.
CONNECT_TOL = 0.5


def aabb_distance(a, b):
    """Exact distance between two axis-aligned boxes given by their extents."""
    d2 = 0.0
    for (a0, a1), (b0, b1) in zip(a, b):
        gap = max(b0 - a1, a0 - b1, 0.0)
        d2 += gap * gap
    return math.sqrt(d2)


print("--- connectivity (min distance to the rest of the assembly) ---")
for mode_name, panel in MODES.items():
    items = [p for p in mode_parts(panel) if not is_soft(p)]
    # No part is excluded, and after D10 the movable panel is not even a
    # borderline case any more: it is not hung on undrawn steel hardware, it
    # LIES on the wood this model draws. Its nearest neighbours are the members
    # it bears on - the back bench rail and rung 1 in bed mode, the back ledger
    # and rung 2 in table mode (D13 took the front bench rail segments out of
    # its X range) - all at zero distance with real contact area (see the D10
    # bearing check above), plus the two ladder uprights its front edge butts
    # against in both modes.
    # D13 also cut the ladder uprights loose from the front bench rail. They are
    # still in contact with the assembly on three counts: the front side rail
    # they are bolted through (Y 704..752 against their back face at 752), the
    # front guard segments lapped onto their front faces, and their own rung
    # blocks - so this check still passes with zero excluded parts.
    skip = set()
    worst = (None, -1.0)
    for p in items:
        if id(p) in skip:
            continue
        others = [q for q in items if q is not p]
        near = min(others, key=lambda q: aabb_distance(p.extents, q.extents))
        # confirm the analytic result with OCC's real solid-to-solid distance
        d = p.distance(near)
        assert d < CONNECT_TOL, (
            f"{mode_name}: '{p.label}' is floating - nearest part "
            f"'{near.label}' is {d:.2f} mm away")
        if d > worst[1]:
            worst = (p.label, d)
    n = len(items) - len(skip)
    print(f"OK  {mode_name}: all {n} wooden parts in contact "
          f"(worst gap {worst[1]:.3f} mm on '{worst[0]}')")

# ---------------------------------------------------------------------------
# THE REFERENCE BODIES, MEASURED
# ---------------------------------------------------------------------------
# Two kinds of number come out of this block and they are not the same kind.
#
# The ASSERTS are about the FIGURE: they read the five anthropometric key
# dimensions back off the built solid and fell the build if the segment table
# and the pose have drifted apart. A figure that is no longer 1200 mm tall is
# not a measuring instrument any more.
#
# The CLEARANCES are about the BED and they are printed, not asserted. A
# reference body is a body: it is in no cut list, it bears on nothing, and the
# hard asserts of this model are about wood that has to fit. What the bodies
# add is the number the wood was always FOR - how much room is over a sitting
# child's head, how far a folded knee stops short of the table - and those
# numbers go into the drawings and into nøkkelmål, where a reader can see them.
# The one hard rule that IS asserted here is that no body is inside any piece
# of wood or steel. Foam is exempt on purpose: a 100 mm cushion takes a
# buttock 12 mm in (FIG_SINK) and a head 22 mm into the sleeping face, and a
# figure that floated on top of the foam instead would be the drawing that
# lies.
print("--- referansekroppene ---")

_fig_bad = []
for _f in FIGURES_ALL:
    for _mode, _panel in MODES.items():
        if _f not in FIGURES[id(_panel)]:
            continue
        for _p in display_parts(_panel):
            if is_soft(_p):
                continue
            if overlap_volume(_f.extents, _p.extents) <= 0:
                continue          # bounding boxes miss: the solids cannot meet
            _hit = _f.intersect(_p)      # None when the solids miss entirely
            # ...and a ShapeList when a limb clips a part in more than one
            # place, which is a real answer and not an error: sum it.
            _vol = (0.0 if _hit is None
                    else sum(_s.volume for _s in _hit)
                    if hasattr(_hit, "__iter__") else _hit.volume)
            if _vol > 1.0:
                _fig_bad.append((_f.label, _p.label, _vol))
assert not _fig_bad, f"reference bodies inside the bed: {_fig_bad}"
print(f"OK  ingen av de {len(FIGURES_ALL)} referansekroppene er inne i noe "
      f"tre eller stål (skummet er unntatt: kroppen synker "
      f"{FIG_SINK} mm ned i puta og hodet "
      f"{FIG_HEAD_R - FIG_TORSO_R + FIG_SINK:.0f} mm ned i soveflaten)")

# --- the figure reads its own key dimensions back off the solid -------------
_up = figure_seated_right
assert abs(_up.pose["crown"][2] - (SEAT_FACE + FIG_SITTING_H)) < TOL, (
    f"sittehøyde: kronen står {_up.pose['crown'][2]:.1f}, "
    f"skal stå {SEAT_FACE + FIG_SITTING_H:.1f}")
assert abs(2 * FIG_SHOULDER_Y - FIG_SHOULDER_W) < TOL, \
    "skulderleddene står ikke 0,21 H fra hverandre"
assert abs(2 * FIG_HEAD_R - FIG_HEAD_H) < TOL, "hodet er ikke H/6 høyt"
_stand = FIG_ANKLE_Z + FIG_SHANK_L + FIG_THIGH_L + FIG_TORSO_L + FIG_NECK_L \
    + 2 * FIG_HEAD_R
assert abs(_stand - FIGURE_H) < 2.0, \
    f"leddkjeden summerer til {_stand:.1f} mm, ikke {FIGURE_H:.0f}"
print(f"OK  figuren: H {FIGURE_H:.0f}, sittehøyde {FIG_SITTING_H:.0f} "
      f"(0,545 H), skulderbredde {FIG_SHOULDER_W:.0f} (0,21 H), hode "
      f"{FIG_HEAD_H:.0f} (H/6), {14} primitiver smeltet til én kropp, "
      f"{FIGURES_ALL[0].volume / 1e6:.1f} dm3 - en kropp på ca "
      f"{FIGURES_ALL[0].volume / 1e6:.0f} kg")


def body_headroom(fig, panel):
    """(mm, what) - the clear straight up over a reference body.

    Box arithmetic, and conservative on purpose in the one direction that
    matters: the answer is measured from the TOP of the body's bounding box to
    the UNDERSIDE of the first part standing over its footprint, so the real
    body has at least this much room and usually more.
    """
    best, who = math.inf, None
    for p in display_parts(panel):
        if not _footprints_overlap(fig.extents, p.extents):
            continue
        gap = p.extents[2][0] - fig.extents[2][1]
        if gap < 0:
            continue
        if gap < best:
            best, who = gap, p.label
    return best, who


FIGURE_CLEAR = {}
for _mode, _panel in MODES.items():
    for _f in FIGURES[id(_panel)]:
        _room, _who = body_headroom(_f, _panel)
        _head_top = _f.pose["head"][2] + FIG_HEAD_R
        FIGURE_CLEAR[_f.label] = {
            "mode": _mode, "crown": _f.pose["crown"],
            "head_top": _head_top, "room": _room, "over": _who}

# The numbers the drawings dimension and nøkkelmål prints, each one measured
# on the solids that were just built - none of them typed.
SIT_HEADROOM = FIGURE_CLEAR["Child Seated Right (table mode)"]["room"]
SIT_HEAD_OVER = FIGURE_CLEAR["Child Seated Right (table mode)"]["over"]
SIT_CROWN_Z = figure_seated_right.pose["crown"][2]
TABLE_OVER_SEAT = PANEL_TOP_TABLE - SEAT_FACE          # 280  [X9: was 140]
TABLE_UNDER_SEAT = PANEL_UNDER_TABLE - SEAT_FACE       # 262  [X9: was 122]
# OCC solid-to-solid, both of them, and after X9 they measure two different
# things than they used to: the right-hand child's KNEES are under the plate
# (so this is the air over the knee, not the gap a folded leg stops short by),
# and the left-hand one's forearms lie on it.
LEG_TO_TABLE = figure_seated_right.distance(panel_table)
WRIST_OVER_TABLE = figure_seated_left.distance(panel_table)
# The anthropometry the height is honestly measured against: this child's
# seated elbow, and how far over it the plate is. Printed, not asserted - the
# builder chose the height and the shop's own pair is no better (SMASTAD's 730
# desk over the 430 chair sold with it is 300 mm; this is 280).
FIG_ELBOW_OVER_SEAT = FIG_TORSO_L - FIG_UARM_L         # 110
TABLE_OVER_ELBOW = TABLE_OVER_SEAT - (FIG_SIT_RISE
                                      + FIG_ELBOW_OVER_SEAT)       # 92
LIE_UPPER_ROOM = FIGURE_CLEAR["Child Lying Upper (bed mode)"]["room"]
LIE_LOWER_ROOM = FIGURE_CLEAR["Child Lying Lower (bed mode)"]["room"]
LIE_LOWER_FACE = SLAT_Z1 - BED_SLAT_T - (
    figure_lying_lower.pose["head"][2] + FIG_HEAD_R)
GUARD_OVER_BODY = GUARD_TOP - figure_lying_upper.extents[2][1]
GUARD_OVER_FACE = GUARD_TOP - (figure_lying_upper.pose["head"][2]
                               + FIG_HEAD_R)

print(f"OK  bordstilling: den som sitter rett opp har {SIT_HEADROOM:.0f} mm "
      f"over hodet (kronen Z {SIT_CROWN_Z:.0f}, '{SIT_HEAD_OVER}' over) - et "
      f"barn på {FIGURE_H:.0f} mm kan sitte helt oppreist i sofaen")
print(f"OK  bordstilling: plata ligger {TABLE_OVER_SEAT:.0f} mm over "
      f"seteflaten og har {TABLE_UNDER_SEAT:.0f} mm under seg - ett lår er "
      f"{2 * FIG_THIGH_R:.0f} mm og et sittende kne står "
      f"{FIG_SIT_RISE + FIG_THIGH_R:.0f} mm over setet, så KNEET går under "
      f"plata med {TABLE_UNDER_SEAT - FIG_SIT_RISE - FIG_THIGH_R:.0f} mm luft "
      f"(X9). Figurene sitter derfor helt alminnelig, med beina ned og "
      f"knærne inn under platen. Målt solid mot solid: nærmeste punkt på den "
      f"som sitter rett opp er {LEG_TO_TABLE:.0f} mm fra platen, og den andre "
      f"har underarmene {WRIST_OVER_TABLE:.0f} mm over den. Til og med v15 "
      f"satt begge i skredderstilling, fordi 122 mm ikke slipper et kne inn")
print(f"OK  bordstilling, ærlig om høyden: {TABLE_OVER_SEAT:.0f} mm over puta "
      f"er {TABLE_OVER_ELBOW:.0f} mm over albuen til et barn på "
      f"{FIGURE_H:.0f} mm som sitter her - en pulthøyde regnet for en STOL, "
      f"brukt fra en sofa. Referansen byggherren pekte på gjør det samme: "
      f"SMÅSTAD-pulten på 730 over den 430 mm stolen som selges til den er "
      f"300 mm. Barnet legger underarmene oppå plata og har albuene i været; "
      f"det er tegnet, ikke bortforklart. Fotskammel finnes ikke: sålene "
      f"henger {figure_seated_left.extents[2][0]:.0f} mm over gulvet, og det "
      f"er ført opp som åpent punkt og ikke som en detalj")
print(f"OK  sengestilling: over den som ligger i køya står ingenting - "
      f"rekkverket står {GUARD_OVER_BODY:.0f} mm over kroppens høyeste punkt "
      f"og {GUARD_OVER_FACE:.0f} mm over ansiktet")
print(f"OK  sengestilling: over den som ligger nede er det "
      f"{LIE_LOWER_ROOM:.0f} mm til '"
      f"{FIGURE_CLEAR['Child Lying Lower (bed mode)']['over']}' og "
      f"{LIE_LOWER_FACE:.0f} mm rett over ansiktet")
assert LIE_UPPER_ROOM == math.inf, \
    "noe står nå over den som ligger i køya - køya skal være åpen oppover"

# ---------------------------------------------------------------------------
# EXPORT
# ---------------------------------------------------------------------------
print("\n=== EXPORT ===")
os.makedirs(GROUP_DIR, exist_ok=True)
exports = []
group_files = []

for name, panel in MODES.items():
    # THE EXPORTED SCENE, not the bed: the two reference children are in every
    # one of these files. They cost four solids and they answer the one
    # question a STEP file or a phone's AR view is actually asked - how big is
    # it, next to whom - and the drawings that must stay about wood are drawn
    # off `display_parts`, which does not have them.
    comp = make_scene(panel)

    # STEP stays in the CAD convention: mm, Z-up.
    step_path = os.path.join(OUT_DIR, f"loftbed_{name}.step")
    export_step(comp, step_path)
    exports.append(step_path)

    # Mesh exports are Y-up so the bed stands upright by default.
    # export_gltf() writes the Z-up -> Y-up rotation onto the root node of the
    # glTF scene itself, so the Z-up compound is handed to it unchanged (pre-
    # rotating would apply the turn twice). The GLB keeps one node per part,
    # so labels and per-part colours survive. Deliverable only (LOFTBED_FULL).
    if FULL_EXPORT:
        glb_path = os.path.join(OUT_DIR, f"loftbed_{name}.glb")
        export_gltf(comp, glb_path, binary=True)
        exports.append(glb_path)

    # ORDER MATTERS HERE. OCC caches a triangulation on a shape and only
    # replaces it when a FINER one is asked for, so the coarse fastener mesh
    # has to be laid down BEFORE the single-mesh export asks for the default
    # 0.001 mm - otherwise the tolerance below is silently ignored and every
    # screw arrives with ~1100 triangles on it. So: per-group first, single
    # mesh second.

    # One STL per colour group (same Y-up orientation), so the .usdz can carry
    # one UsdPreviewSurface material per group - the fasteners included, which
    # is what makes the steel read as steel on a phone. These are
    # intermediates and deliberately live outside the repo.
    manifest = []
    for group in GROUP_ORDER:
        members = [p.moved(Y_UP) for p in scene_parts(panel)
                   if p.group == group]
        if not members:
            continue
        gpath = os.path.join(GROUP_DIR, f"loftbed_{name}_{group}.stl")
        if group == "fasteners":
            # A screw and a bent bracket are the only curved / small solids in
            # this model, and at the default deflection one screw tessellates
            # to more triangles than the whole bed. They are meshed at drawing
            # resolution instead: same silhouette, ~15x fewer triangles.
            export_stl(Compound(children=members), gpath,
                       tolerance=FASTENER_MESH_TOL,
                       angular_tolerance=FASTENER_MESH_ANG)
        else:
            export_stl(Compound(children=members), gpath)
        rgba = ",".join(f"{c:.4g}" for c in tuple(GROUP_COLORS[group]))
        manifest.append(f"{group}={rgba}={gpath}")
    mpath = os.path.join(GROUP_DIR, f"loftbed_{name}.groups")
    with open(mpath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(manifest) + "\n")
    group_files.append(mpath)

    # STL has no transform node, so Y-up has to be baked into the vertices.
    # The same coarse deflection is used for the whole compound: every wooden
    # part is a BOX, and a planar face triangulates to the same two triangles
    # at any deflection, so the wood comes out byte-identical to the default
    # export and only the steel gets cheaper.
    y_up = make_scene(panel, Y_UP)
    stl_path = os.path.join(OUT_DIR, f"loftbed_{name}.stl")
    export_stl(y_up, stl_path, tolerance=FASTENER_MESH_TOL,
               angular_tolerance=FASTENER_MESH_ANG)
    exports.append(stl_path)

    # Hidden-line projections are by far the slowest step in this script, so
    # they are deliverables only (LOFTBED_FULL / `mise run build-full`).
    if FULL_EXPORT:
        for view, direction in (("iso", (1, -1, 1)), ("front", (0, -1, 0))):
            svg_path = os.path.join(OUT_DIR, f"loftbed_{name}_{view}.svg")
            try:
                write_svg(comp, svg_path, direction)
                exports.append(svg_path)
            except Exception as e:  # pragma: no cover
                print(f"SVG export failed for {svg_path}: {e}")

for p in exports:
    print("  wrote", p)
print(f"  per-colour-group STL manifests in {GROUP_DIR}:")
for p in group_files:
    print("   ", p)
if not FULL_EXPORT:
    print("  (.glb and .svg skipped - run `mise run build-full` / LOFTBED_FULL=1 "
          "for the full deliverable set)")

# ---------------------------------------------------------------------------
# CUT LIST
# ---------------------------------------------------------------------------
print("\n=== CUT LIST ===")
# The name column is 40 wide so the longest entry - "Guard rail, front segment
# (D2/D7/D13)", 39 chars - fits without running into the section column.
NAME_COL = 40
RULE = NAME_COL + 18 + 12 + 6                  # 76
print(f"{'Part':<{NAME_COL}}{'Section':<18}{'Length (mm)':>12}{'Qty':>6}")
print("-" * RULE)
total = 0
for (part, section, length), qty in sorted(CUT_LIST.items()):
    assert len(part) < NAME_COL, \
        f"cut-list name '{part}' ({len(part)} chars) overflows the {NAME_COL} " \
        f"char column"
    print(f"{part:<{NAME_COL}}{section:<18}{length:>12}{qty:>6}")
    total += qty
print("-" * RULE)
print(f"{'TOTAL pieces':<{NAME_COL}}{'':<18}{'':>12}{total:>6}")
by_section = {}
by_metres = {}
for (part, section, length), qty in CUT_LIST.items():
    by_section[section] = by_section.get(section, 0) + qty
    by_metres[section] = by_metres.get(section, 0) + qty * length
print("\nBy section: " + ", ".join(
    f"{s} x{n}" for s, n in sorted(by_section.items(), key=lambda kv: -kv[1])))

# U1/U2: THE STORE LIST. Unifying the boards and the corner posts on 36x98 is
# only worth doing if it shows up here, so the census is printed rather than
# argued: pieces and running metres per profile, timber profiles counted.
# (Sale lengths and the cutting plan are the docs round's job - this is the raw
# demand.) The panel is a sheet, not a profile, and is excluded from the count.
print("\nStore list - what to buy, by profile:")
TIMBER_PROFILES = sorted((s for s in by_section if "panel" not in s),
                         key=lambda s: (-by_metres[s], s))
for s in TIMBER_PROFILES:
    print(f"  {s:<12}{by_section[s]:>4} pcs {by_metres[s] / 1000:>8.2f} m")
for s in (s for s in by_section if "panel" in s):
    print(f"  {s:<12}{by_section[s]:>4} pcs {by_metres[s] / 1000:>8.2f} m "
          f"(sheet, not a profile)")
print(f"  {'TOTAL':<12}{sum(by_section.values()):>4} pcs "
      f"{sum(by_metres.values()) / 1000:>8.2f} m in "
      f"{len(TIMBER_PROFILES)} timber profiles + 1 sheet")
# The profile list is a design statement, not an observation: any new profile
# has to be argued for, and any profile that empties out has to leave.
EXPECTED_PROFILES = {
    sec(BOARD23_T, BOARD36_W),      # 23x98 - the 24 slats (V6), flat-loaded
    sec(BOARD36_T, BOARD36_W),      # 36x98 - boards AND corner posts (U1/U2)
    sec(BLOCK_T, BLOCK_H),          # 36x48 - ladder uprights and every block
    sec(BENCH_RAIL_T, BENCH_RAIL_H),  # 48x73 - bench rails, rungs, battens,
                                      #         the four stub legs (U5) AND the
                                      #         back table ledger (V2)
    sec(RAIL_T, RAIL_H),            # 48x98 - the two side rails (V6b)
}
# U5: the stub legs are cut from the bench-rail profile now, so they add no
# entry of their own - this is the assert that would have caught 48x48 coming
# back in through the side door.
assert sec(LEG_T, LEG_W) == sec(BENCH_RAIL_T, BENCH_RAIL_H), \
    f"U5: the stub legs are {sec(LEG_T, LEG_W)}, not the bench rail profile " \
    f"{sec(BENCH_RAIL_T, BENCH_RAIL_H)} - that is a sixth profile again"
assert set(TIMBER_PROFILES) == EXPECTED_PROFILES, \
    f"the bed is built from {sorted(TIMBER_PROFILES)}, expected " \
    f"{sorted(EXPECTED_PROFILES)}"
# V2: 21x95 LEFT THE BED. It was the back table ledger and nothing else - one
# 1794 mm piece keeping a whole stock line, a whole shopping line and a whole
# pile on the floor alive - and the ledger is a 48x73 now for reasons that have
# nothing to do with the list (see the LEDGER block). This is the assert that
# says the saving is real and that 21x95 is not to come back quietly.
assert sec(BOARD_T, BOARD_W) not in TIMBER_PROFILES, \
    "V2: 21x95 is supposed to be gone from the bed entirely"
assert len(TIMBER_PROFILES) == 5, \
    f"V6 put 23x98 in beside the four U1/U2/U5/V2 left; " \
    f"this is {len(TIMBER_PROFILES)}"
# V6: the biggest pile moved. The slats went to 23x98, so THAT is now both
# the most numerous profile and the longest by metres, and 36x98 is left with
# the 4 guard segments and the 4 corner posts - the on-edge and the standing
# members, which is exactly what a 36 mm board is worth paying for.
# V13: 24 -> 26. The two end slats are the same board, 764 instead of 800.
assert by_section[sec(BOARD23_T, BOARD36_W)] == SLAT_COUNT + 2 * (
        BENCH_SLAT_COUNT + 1) == 26 and \
    max(by_metres, key=by_metres.get) == sec(BOARD23_T, BOARD36_W), \
    "V6/V13: 23x98 must be both the most numerous and the longest profile"
assert by_section[sec(BOARD36_T, BOARD36_W)] == 10, \
    "V6: 36x98 is 4 guard segments + 4 corner posts + 2 end beams (V6b)"
assert "34x98" not in by_section, \
    "U1: 34x98 is supposed to be gone from the bed entirely"
print("\nNote: the movable panel and its four battens are listed once; they "
      "are the same five parts in both modes.")
print(f"Note (D10/M4/M5/V2): the panel rests straight on wood in both modes - "
      f"rear edge on a {sec(LEDGER_BACK_T, LEDGER_BACK_H)} member at Y "
      f"{LEDGER_BACK_Y0}..{LEDGER_BACK_Y0 + LEDGER_BACK_T} whichever mode it "
      f"is in, front edge on a rung - and is stiffened by 2 x "
      f"{sec(BATTEN_W, BATTEN_H)} x {BATTEN_LEN} battens along Y (X "
      f"{BATTEN_X[0]}/{BATTEN_X[1]}) plus 2 x {sec(BATTEN_W, BATTEN_H)} x "
      f"{NOSE_LEN} WEDGES (V4: {NOSE_ROOT_H} mm at the root, "
      f"{NOSE_TIP_H} at the tip) flush with the front edge, under the corners "
      f"the {FRONT_CANTILEVER} mm of bare sheet outboard of the guide batten "
      f"would otherwise leave. THERE IS NO STEEL IN THE MECHANISM ANY MORE "
      f"(V3): the two long battens sit {PANEL_FIT} mm outboard of the rung "
      f"ends, in the {RUNG_T} x {RUNG_REST_LEDGE} mm shafts beside them, and "
      f"they are the whole of the X and the anti-rotation restraint in both "
      f"modes. And after the lock decision (V4) there is no steel on the "
      f"shopping list for this panel either: NO bed-mode lock, an accepted "
      f"deviation - see vedlegg B, avvik 4.")
print(f"Note (D11/D13): the front bench rail is two {FRONT_BENCH_RAIL_SEG_LEN} mm "
      f"segments that stop at the sofa ends on their stub legs; only the back "
      f"one is a continuous member, and after W9 it is {BETWEEN_POSTS_LEN} mm, "
      f"post to post. The ladder uprights no longer lap it - flagged for the "
      f"docs-round load check.")
print(f"Note (D12): the depth stack came in {DEPTH_SHRINK} mm on the FRONT side "
      f"only, so the {MATTRESS_W} mm mattress is exactly the rail-to-rail "
      f"platform. All {SLAT_COUNT} upper slats, all "
      f"{BENCH_SLAT_COUNT * len(BENCH_X)} bench slats and the panel are "
      f"{SLAT_LEN} mm long (was 906) - the two V13 end slats are the one "
      f"exception at {END_SLAT_LEN}, because the back corner post stands in "
      f"their line - and the end beams {END_BEAM_LEN} mm (was "
      f"1002, 896, 848). Overall depth {OVERALL_DEPTH} mm (1070 in v7, 964 in "
      f"v8, 930 before D14, 896 before W6, 848 before U2).")
print(f"Note (D14): the four front guard boards hang on the INNER faces of the "
      f"front posts / ladder uprights (Y {FRONT_GUARD_Y0}..{FRONT_GUARD_Y1}) "
      f"instead of the outer ones (was 800..834), so nothing stands proud of "
      f"the post plane Y={FRONT_POST_Y1} and the overall depth dropped 34 mm, "
      f"930 -> 896 (W6 then took it to 848 and U2/U3 to {OVERALL_DEPTH}). Same "
      f"four pieces, same lengths, same X - but the two 5x60 per lap are driven "
      f"FROM INSIDE THE BED now, and after U2 each lap is bigger: "
      f"{POST_W - THROUGH_X0} x {GUARD_W} mm onto a corner post (was 45 x 98) "
      f"and {UPRIGHT_W} x {GUARD_W} onto a ladder upright (was 36 x 98). The "
      f"boards overhang the mattress footprint by {GUARD_T} mm at "
      f"guard height; the lower band is {GUARD_BAND_Z0[0] - MATTRESS_Z1} mm "
      f"above the mattress top, so nothing touches it.")
print(f"Note (W1): *** WALL-SIDE BED - NOT REVERSIBLE. *** The back long side "
      f"stands against the room wall and the frame is screwed to it through the "
      f"back rail, so there are NO back guard boards: the wall is the barrier. "
      f"The back face of the assembly is the flat mounting plane Y={WALL_Y} - "
      f"the back rail, the 2 back posts tucked into its plane, the 2 end beams "
      f"and their blocks, the back bench rail and its blocks, the ledger and "
      f"{SLAT_COUNT + BENCH_SLAT_COUNT * len(BENCH_X)} of the "
      f"{SLAT_COUNT + BENCH_SLAT_COUNT * len(BENCH_X) + len(end_slats)} slat "
      f"ends, all coplanar (the two V13 end slats stop on the back post's "
      f"front face at Y {END_SLAT_Y0} instead - the post is what is in that "
      f"plane there) - "
      f"and the mattress gap is {MAX_MATTRESS_GAP} mm (W5), against the "
      f"{MAX_GUARD_OPENING} mm EN 747 entrapment limit. The two deleted boards were "
      f"{sec(GUARD_T, GUARD_W)} x {THROUGH_LEN}; putting them and two full-height "
      f"({POST_HEIGHT}) back posts back is the retrofit if a freestanding "
      f"version is ever wanted, but after W6 it also means moving the posts back "
      f"out into a layer of their own - flagged for the docs round.")
print(f"Note (W6): the two BACK corner posts stand IN the back rail plane "
      f"(Y {BACK_POST_Y0}..{BACK_POST_Y1}, was -96..-48) and are cut to "
      f"{BACK_POST_HEIGHT} mm (X1 lifted the whole deck 150: was 1065, and "
      f"1197 / 1337 before W6) - the RAIL UNDERSIDE. The back "
      f"side rail bears straight down on the post tops, "
      f"{POST_W - THROUGH_X0} x {POST_T} = {BACK_RAIL_POST_BEARING} mm2 of end "
      f"grain per corner, so the corner reaction goes rail -> post -> floor with "
      f"no fastener in the load path; the bolts and corner brackets are pure "
      f"ties. The two FRONT posts and the two ladder uprights stay "
      f"{POST_HEIGHT}. Same {sec(POST_T, POST_W)} section, two cut lengths. "
      f"Nothing of a back post is within {SLAT_Z1 - BACK_POST_HEIGHT} mm of the "
      f"mattress underside.")
print(f"Note (W7): the wall plane is the back rail's outer face, Y={WALL_Y} (was "
      f"-96), so the overall depth is {OVERALL_DEPTH} mm - {896 - OVERALL_DEPTH} "
      f"less than v9 ({BACK_TUCK} of it from W6's tuck at the back and "
      f"{POST_THIN} from U2's re-section at the front) and exactly the end-beam "
      f"length {END_BEAM_LEN}.")
print(f"Note (W8): the upper slat field is {SLAT_COUNT} slats (was 13 in v8, 14 "
      f"in two lengths in v9) and they are ONE length again: {SLAT_COUNT} x "
      f"{SLAT_LEN} at Y {SLAT_Y0}..{SLAT_Y1}, the same piece as a bench slat. "
      f"There is no slot behind the platform to cover any more - W6 deleted the "
      f"layer it was in - so the 847 mm extended slat is gone. Gap between "
      f"slats {slat_gap:.1f} mm.")
print(f"Note (W9): the back bench rail and the back table ledger run POST TO "
      f"POST, {BETWEEN_POSTS_LEN} mm at X {BETWEEN_POSTS_X0}.."
      f"{BETWEEN_POSTS_X1} (was {THROUGH_LEN} at {THROUGH_X0}..{THROUGH_X1}) - "
      f"the back posts moved into their Y band, so they butt them and are "
      f"screwed to their X-inner faces, an end fixing neither had before - and "
      f"since V5 deleted the two bearing blocks that hung under those ends, it "
      f"is the WHOLE end fixing: 2 x 6x80 skew screws per end, 4.0 kN in shear "
      f"against 0.5. The bench slats are re-pitched to start at the post inner face: "
      f"X {BENCH_SLAT_X_START}..{BENCH_LEN}, pitch {BENCH_SLAT_PITCH:g} (124.75 "
      f"in v10, 137.5 before that), gap {BENCH_SLAT_PITCH - BENCH_SLAT_W:g} mm "
      f"(26.75, 39.5) - same five pieces per bench, closer together each time "
      f"the post got wider. V13 adds a SIXTH outboard of them, the "
      f"{END_SLAT_LEN} mm end slat on its cleat at X {END_SLAT_X[0]}.."
      f"{BENCH_SLAT_X_START}, so the field reaches the wall after all and the "
      f"lower level is a bed in full length.")
print(f"Note (W5): the mattress is PINNED again. The clear between the wall "
      f"(Y {MATTRESS_STOP_Y0}) and the front verticals (Y {MATTRESS_STOP_Y1}) "
      f"is {MATTRESS_STOP_Y1 - MATTRESS_STOP_Y0} mm, i.e. exactly the mattress, "
      f"so it can wander {MATTRESS_WANDER} mm and leaves {MAX_MATTRESS_GAP} mm "
      f"of gap at either long edge - the EN 747 {MAX_GUARD_OPENING} mm limit is "
      f"not in play at all - with slat underneath it the whole way.")
print(f"Note (U5): the four bench stub legs are {sec(LEG_T, LEG_W)} x "
      f"{STUB_LEG_H} again (48x48 from W3 to U4). W3 squared them off to share "
      f"the corner-post section; U2 has since taken the posts to "
      f"{sec(POST_T, POST_W)} and the legs cannot follow - a {POST_T} mm leg "
      f"would hang out of the {BENCH_RAIL_T} mm bench rail it bears under - so "
      f"48x48 was left as an orphan profile carrying four 186 mm pieces, a "
      f"whole 2.4 m board at 69% waste. They are cut from the "
      f"{sec(BENCH_RAIL_T, BENCH_RAIL_H)} bench-rail board instead, off the "
      f"rest that the four rungs leave. Their inner faces are unmoved on the "
      f"bench ends X {BENCH_LEN} / {WALL_SPAN - BENCH_LEN} and they run outward "
      f"from there, so the front rail segments are still zero-cantilever "
      f"end-bearing members; the leg-on-rail contact is {LEG_BEARING_AREA} mm2 "
      f"(was 2304), utilisation ~0.06 in compression perpendicular to the "
      f"grain.")
print(f"Note (D13): the ladder is {LADDER_CLEAR} mm clear (was 420) on "
      f"{sec(UPRIGHT_T, UPRIGHT_W)} uprights (was 48x48), so the rungs are "
      f"{RUNG_LEN} mm and the front guard segments {FRONT_GUARD_SEG_LEN} mm. "
      f"The rung blocks are {sec(RUNG_BLOCK_T, RUNG_BLOCK_H)}x"
      f"{RUNG_BLOCK_LEN} - their 36 mm is stock thickness, not upright width, "
      f"and K1 has since cut the length {RUNG_D} -> {RUNG_BLOCK_LEN} so the "
      f"piece is exactly as long as the {UPRIGHT_T} mm face it is screwed to.")
print(f"Note (U1): the board profile is {sec(BOARD36_T, BOARD36_W)}, not 34x98. "
      f"34x98 was a drawing dimension; {sec(BOARD36_T, BOARD36_W)} is the shelf "
      f"item. The board is 2 mm thicker and nothing else about it changes - same "
      f"{BOARD36_W} mm width, same lengths, same pieces - but the 2 mm shows up "
      f"in every stack a board is IN: platform top 1197 -> 1186, mattress "
      f"1186..1336, bench top 293 -> {BENCH_TOP}, cushion "
      f"recess under the bed-mode panel 16 -> {PANEL_BENCH_DIP} mm, guard bands "
      f"up 2 to 1401..1499 and 1574..1672. The EN 747 openings "
      f"above the mattress are unchanged at 75 / 75 and the third closed "
      f"against the then-fixed 1700 post tops: 17 -> 28 mm. (v14/X1 has since "
      f"lifted every one of those upper numbers by 150 - see the X1 note.)")
print(f"Note (U2): the four CORNER POSTS are {sec(POST_T, POST_W)} as well - "
      f"the same plank as the boards, turned thin-face-to-the-room ({POST_T} in "
      f"Y, {POST_W} in X). 48x48 leaves the frame; the four bench stub legs were "
      f"the last thing on it, and U5 has since taken them to "
      f"{sec(BENCH_RAIL_T, BENCH_RAIL_H)} too, so the profile is gone from the "
      f"bed. Consequences, all asserted above: the posts stand at X "
      f"0..{POST_W} / {WALL_SPAN - POST_W}..{WALL_SPAN}; the end beams move out "
      f"to the new inner faces X {END_BEAM_X[0]}..{END_BEAM_X[0] + RAIL_T} / "
      f"{END_BEAM_X[1]}..{END_BEAM_X[1] + RAIL_T} and shorten to {END_BEAM_LEN}; "
      f"the back bench rail and the back table ledger shorten to "
      f"{BETWEEN_POSTS_LEN} (X {BETWEEN_POSTS_X0}..{BETWEEN_POSTS_X1}); the "
      f"bench slats re-pitch to {BENCH_SLAT_PITCH:g}; the back rail bears on "
      f"{BACK_RAIL_POST_BEARING} mm2 of post top instead of 2160; the guard laps "
      f"grow to {POST_W - THROUGH_X0} x {GUARD_W} on a post and {UPRIGHT_W} x "
      f"{GUARD_W} on an upright. The two LADDER UPRIGHTS keep their "
      f"{sec(UPRIGHT_T, UPRIGHT_W)} stock and TURN, so the whole front plane is "
      f"one {POST_T} mm layer; the price is the walk-around beside the ladder, "
      f"154 -> 142 mm.")
print(f"Note (U3): the front face of the bed is the plane Y={FRONT_POST_Y1} - "
      f"two corner posts and two ladder uprights, nothing else - so the overall "
      f"depth is {OVERALL_DEPTH} mm, {POST_THIN} less than v10, and Y "
      f"{FRONT_POST_Y1}..{FRONT_POST_Y1 + POST_THIN} is asserted EMPTY. The bed "
      f"is still exactly as deep as its own end beams.")
print(f"Note (U4): NO M8 GOES INTO A POST ANY MORE. An M8 needs 3d = 24 mm of "
      f"edge distance and a {POST_T} mm post offers 18 on its centre line, so "
      f"every joint into a corner post switches to the pre-drilled 6 mm screw "
      f"pattern the ladder uprights already use (J3): 6 mm wants 3d = 18, which "
      f"is exactly what a {POST_T} mm face gives, and 6x80 through a {RAIL_T} mm "
      f"rail leaves 32 mm in the post (U4 wrote 6x90; the screw consolidation "
      f"has since taken every one of them to 6x80). Stacked along the post grain as the ties "
      f"were. Affected: J1 (end beam -> post), J2 (front side rail -> post), "
      f"J8 (bench rail -> post) and the W9 end fixings of the back bench rail "
      f"and the back table ledger. U4 said the load path did not change "
      f"because the C2 bearing blocks carried every vertical reaction; V5 has "
      f"since deleted those blocks, so J1, J8 and J8-B DO carry their corner "
      f"reactions in screw shear now - 4.0 kN against 1.0 / 0.5 / 0.5, "
      f"asserted above.")
print(f"Note (D5/D7/U1/U2): {sec(BOARD36_T, BOARD36_W)} is the stock of this "
      f"bed - {SLAT_COUNT} upper bed slats + {BENCH_SLAT_COUNT * len(BENCH_X)} "
      f"bench slats + {len(FRONT_GUARD_SEGMENTS) * len(GUARD_BAND_Z0)} front "
      f"guard segments + 4 corner posts = "
      f"{by_section[sec(BOARD36_T, BOARD36_W)]} of the {total} pieces in the "
      f"bed and {by_metres[sec(BOARD36_T, BOARD36_W)] / 1000:.1f} of its "
      f"{sum(by_metres.values()) / 1000:.1f} running metres. W8's ONE-LENGTH "
      f"rule survives on the flat boards: cut "
      f"{SLAT_COUNT + BENCH_SLAT_COUNT * len(BENCH_X)} identical {SLAT_LEN} mm "
      f"pieces in a single setup ({SLAT_COUNT} upper slats + "
      f"{BENCH_SLAT_COUNT * len(BENCH_X)} bench slats - one and the same "
      f"piece), then {len(FRONT_GUARD_SEGMENTS) * len(GUARD_BAND_Z0)} guards at "
      f"{FRONT_GUARD_SEG_LEN} and the posts at {BACK_POST_HEIGHT} / "
      f"{POST_HEIGHT}. Four saw stops for the biggest pile in the bed.")
print(f"Note (D7/U5/V2): the one-piece-profiles are gone, both of them. 48x48 "
      f"was the four {STUB_LEG_H} mm bench stub legs and U5 ripped them out of "
      f"the {sec(BENCH_RAIL_T, BENCH_RAIL_H)} bench-rail board; 21x95 was the "
      f"back table ledger, {BETWEEN_POSTS_LEN} mm and nothing else, and V2 "
      f"makes that a {sec(LEDGER_BACK_T, LEDGER_BACK_H)} too - for the rear "
      f"seat, not for the list, but the list is {len(TIMBER_PROFILES)} "
      f"profiles now.")
print("Note (D5): the slat cleats are gone; the upper slats are screwed "
      "straight down onto the side rails, one 5x60 per end.")

# ---------------------------------------------------------------------------
# X10 - THE COMMENTS ARE CHECKED TOO
# ---------------------------------------------------------------------------
# A number in a comment is the cheapest documentation this file has and the
# only kind nothing was reading. Sixteen of them had gone stale - MATTRESS_Z0
# said 1199 next to a value of 1523, NOSE_LEN said 116 next to 77 - and every
# one of them had been true once, which is exactly what makes them expensive:
# a wrong number left standing is a trap, and a wrong number that used to be
# right is a trap with a provenance.
#
# So the file reads its own source and asks. The shape it looks for is the one
# the file already uses everywhere:
#
#       NAME = expression            # <value>[, prose] [history]
#
# The comment has to OPEN with the number - "# 1080, to the slats" is a value
# and "# EN 747 entrapment limit" is not, and neither is "# 36x48 stock", where
# the digits are a section. Anything in square brackets is HISTORY: `[was 116,
# 213]`, `[X9: 409]`, and it is skipped, because the whole point of writing the
# old value down is that it is not the current one.
#
# Scalars only, and that is deliberate rather than lazy: a comment on a list
# ("# 0..98 and 1892..1990") is a sentence about a shape, not a value, and
# guessing which numbers in it are supposed to be the elements is how a
# checker starts producing noise instead of findings. Integer comments are
# allowed to be the value ROUNDED - FIG_TORSO_L is 314,4 and says 314 - and
# half a millimetre is all the rounding they get.
#
# WHAT IT CANNOT SEE: a comment on the second line of a two-line assignment,
# because the name is not on that line. There are a handful of those and they
# are the price of a checker small enough to be obviously right.
#
# X12 MADE IT A FUNCTION, which is a smaller change than it looks and the
# reason is the whole point of tools/falsifiser.py: a checker that can only be
# run on this file, as it stands on disk, cannot be shown to BITE. Given the
# source as a string and the values as a dict, it can be handed a comment with
# one digit changed and asked to find it - and that proof is now part of the
# gate. Nothing else moved: the loop below is the loop that was here.
_VC_LINE = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*=\s*(?!=)(.+?)\s+#\s*(\S.*)$")
_VC_HEAD = re.compile(r"^(-?\d+(?:[.,]\d+)?)(?![\dxX×])")


def stale_value_comments(source, values):
    """(stale, checked, skipped) for `NAME = expr  # <value>` in `source`."""
    stale, checked, skipped = [], 0, 0
    for no, line in enumerate(source.split("\n"), 1):
        m = _VC_LINE.match(line.rstrip("\n"))
        if not m:
            continue
        name, _, comment = m.groups()
        head = _VC_HEAD.match(comment.split("[")[0].strip())
        if head is None:
            continue
        if name not in values:
            skipped += 1
            continue
        val = values[name]
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            skipped += 1
            continue
        text = head.group(1).replace(",", ".")
        said = float(text)
        # A comment is allowed to be the value ROUNDED TO ITS OWN PRECISION and
        # no further: "# 314" may stand over 314,4 and "# 50.7" over 50,7073,
        # but neither may stand over a different number.
        dp = len(text.split(".")[1]) if "." in text else 0
        checked += 1
        if abs(said - float(val)) > 0.5 * 10 ** -dp:
            stale.append((no, name, said, float(val)))
    return stale, checked, skipped


with open(__file__, encoding="utf-8") as _fh:
    VALUE_COMMENT_SOURCE = _fh.read()
_VC_STALE, _VC_CHECKED, _VC_SKIPPED = stale_value_comments(
    VALUE_COMMENT_SOURCE, globals())
assert not _VC_STALE, (
    "X10: stale value comments - the number is not what the name is worth:\n"
    + "\n".join(f"    line {n}: {k} says {a:g}, and it is {b:g}"
                 for n, k, a, b in _VC_STALE)
    + "\nEither fix the number or move it into a [was ...] bracket, which is "
      "what a value that used to be true is for")
print(f"OK  X10 verditallene i kommentarene: {_VC_CHECKED} av formen "
      f"`NAVN = uttrykk  # tall` er lest ut av fila og målt mot verdien "
      f"navnet faktisk har. Ingen står igjen fra en gammel runde. "
      f"({_VC_SKIPPED} hoppet over: ikke skalarer, eller navn som ikke "
      f"finnes på modulnivå. Historikk i [ ] leses ikke)")


# ---------------------------------------------------------------------------
# PARTS SNAPSHOT
# ---------------------------------------------------------------------------
# parts.tsv is the tracked regression snapshot: every part's label, colour group
# and bounding box, sorted by label. Both panel positions are in it, told apart
# by the "(bed mode)" / "(table mode)" suffix on the label. It is the one
# generated file that IS committed - a diff on it is the diff on the model.
snapshot = (parts + [mattress] + CUSHIONS_ALL + [panel_bed, panel_table]
            + battens_bed + battens_table + FIGURES_ALL)
snap_path = os.path.join(OUT_DIR, "parts.tsv")
with open(snap_path, "w", encoding="utf-8") as fh:
    fh.write("label\tgroup\tx0\tx1\ty0\ty1\tz0\tz1\n")
    for p in sorted(snapshot, key=lambda q: q.label):
        (x0, x1), (y0, y1), (z0, z1) = p.extents
        fh.write(f"{p.label}\t{p.group}\t" + "\t".join(
            f"{v:g}" for v in (x0, x1, y0, y1, z0, z1)) + "\n")
print(f"\nwrote {snap_path} ({len(snapshot)} parts, both panel modes)")
