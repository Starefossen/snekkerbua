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
U5  THE BENCH STUB LEGS GO BACK TO 48x73 AND 48x48 LEAVES THE BED. v9/W3 had
    squared the four legs off, 48x73 -> 48x48, for exactly one reason: 48x48
    was the corner-post section then, so it consolidated two profiles into
    one. U2 above moved the posts to 36x98 and that reason is gone. What was
    left was an ORPHAN profile: 48x48 bought for four 186 mm pieces and
    nothing else - 744 mm of wood off a 2,4 m board, 69% waste, its own line
    in the shopping list and its own pile on the floor. So the legs revert to
    48x73, which is the BENCH RAIL'S OWN profile - the very member each leg
    bears under - and they are cut from the rest the four rungs leave on the
    2,4 m 48x73 board. The purchase is unchanged (1 x 4,8 m + 1 x 2,4 m of
    48x73), one board and one profile leave the list, and the bed is down to
    FIVE timber profiles plus the plywood sheet.
    The Y dimension - the binding one - never moves: 48, the bench rail's own
    depth, so the leg is flush in Y as it always was. All the change is in X,
    where there is a whole rail to sit under. Consequences:
      leg-on-rail bearing  48 x 48 = 2304 -> 48 x 73 = 3504 mm2, i.e. ~8,0 kN
                           against the ~0,5 kN a leg sees; utilisation
                           0.09 -> 0.06
      X positions          the RULE is unchanged (inner face on the inner end
                           of its own bench, X 645 / 1345, leg running
                           outward from there, fully under its rail segment),
                           so only the outer faces move: 597..645 -> 572..645
                           and 1345..1393 -> 1345..1418
      J10                  the bracket and its screws re-derive against a
                           73 mm leg face instead of 48 - see the joint
    Unchanged: the leg height (186), the bench rail segments, the open front
    floor X 645..1345, the walk-around, and every other profile in the bed.

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
        by the upright getting narrower in X.
    The pair of them opens a walk-around passage on each side of the ladder,
    between the sofa end and the upright outer face, 151 mm clear and empty
    from the floor to 482.
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

Upper level: a 1984 x 800 sleeping platform at 1065 mm underside height (the
slats bridge both rails flush on top, D5; D12 shrank the depth 906 -> 800 so
the 800 mm mattress is flush at both edges), carried by four corner posts -
two 1700 mm ones at the front and, after v10/W6, two 1065 mm ones at the back
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
Z 186..259, carried at their ends by the corner posts (on their own end
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
  * TABLE MODE  - on the back table ledger (top Z 482) and on ladder rung 2
                  (top Z 482); panel top Z = 500.
  * BED MODE    - on the back bench rail (top Z 259) and on ladder rung 1
                  (top Z 259); panel top Z = 277, i.e. 18 mm below the bench
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

# U5: THE FOUR BENCH STUB LEGS GO BACK TO 48x73 - THE BENCH RAIL'S OWN PROFILE.
# The leg is an END BEARING under a bench rail, not a column. What it has to do
# is (a) present enough face to the rail underside and (b) not buckle over its
# own 186 mm. Buckling is a non-question at 186 mm (lambda ~13), so the section
# is decided by the bearing and by the cut list.
# HISTORY. v9/W3 took the leg 48x73 -> 48x48 for one reason only: 48x48 was the
# corner-post section at the time, so the change CONSOLIDATED two profiles into
# one. v11/U2 then took the corner posts to 36x98 and that argument evaporated -
# 48x48 was left as an ORPHAN profile carrying four 186 mm pieces and nothing
# else, i.e. a whole 2.4 m board bought for 744 mm of wood: 69% waste, an extra
# line in the shopping list and an extra pile on the floor. U5 reverses W3. The
# leg is 48x73 again, which is the bench rail's own profile - the very member it
# bears under - so the four legs are cut from the 48x73 board that already has
# 1108 mm of rest on it after the four rungs. One fewer profile, one fewer
# board, no new stock.
# The Y DIMENSION IS THE CONSTRAINT AND IT DOES NOT MOVE: 48, exactly the bench
# rail's depth, so the leg is flush in Y and neither hangs out of the rail nor
# leaves a lip. All the change is in X, where there is a whole rail to sit
# under. At 48x73 the leg-on-rail contact is 48 x 73 = 3504 mm2 (was 2304);
# against f_c90,d with k_c90 = 1.5 that is ~8.0 kN, i.e. utilisation ~0.06 at
# the ~0.5 kN a leg actually sees.
# The X POSITION rule is unchanged and is what the validation block enforces:
# the leg's INNER face lands on the inner end of its bench-rail segment
# (X 645 / 1345), so the rail still has zero cantilever past it, and the whole
# leg stays under that segment. Only the OUTER face moves back out, 597 -> 572
# and 1393 -> 1418 (the pre-W3 positions).
LEG_T = 48           # bench stub legs, thin dim (Y)   - unchanged stock
LEG_W = 73           # bench stub legs, wide dim (X)   [48 in W3..U4; 73 again, U5]

RAIL_T = 48          # upper bed side rails and end beams, thickness
RAIL_H = 98          # upper bed side rails and end beams, height  [was 123]

BENCH_RAIL_T = 48    # continuous bench rails, thickness (Y) - unchanged stock
BENCH_RAIL_H = 73    # continuous bench rails, height (Z)    - unchanged stock

TREAD_T = 48         # ladder rung (tread) thickness (Z) - unchanged stock
TREAD_D = 73         # ladder rung (tread) depth (Y)     - unchanged stock

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
BED_SLAT_T = BOARD36_T   # D5: upper bed slats, thickness (Z)
BED_SLAT_W = BOARD36_W   # D5: upper bed slat width (X)
BENCH_SLAT_T = BOARD36_T # C3: bench slats upgraded 21x95 -> 36x98, thickness (Z)
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
}
GROUP_ORDER = ["posts", "rails", "boards", "panel", "mattress"]

# ---------------------------------------------------------------------------
# ENVELOPE
# ---------------------------------------------------------------------------
WALL_SPAN = 1990                 # X = 0 .. 1990, hard limit
MATTRESS_W = 800                 # 200x80 mattress
MATTRESS_H = 140

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
RAIL_BOTTOM = 1065               # underside of the upper side rails (FIXED)
RAIL_TOP = RAIL_BOTTOM + RAIL_H  # 1163

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
#   * no slat can foul a back post: the posts stop at the rail underside 1065
#     and the slats start at the rail top 1163, 98 mm clear. Asserted anyway;
#   * the 14-slat field survives from W4 (the 13-slat one had 60.5 mm gaps);
#     at this pitch the gap is 44.5 mm.
WALL_Y = BACK_RAIL_Y0                    # -48, the mounting face against the
                                         # wall = the back rail's outer face (W7)
SLAT_Z0 = RAIL_TOP                       # 1163, slats bear on top of the rails
SLAT_Z1 = SLAT_Z0 + BED_SLAT_T           # 1199
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
MATTRESS_Z0 = SLAT_Z1                    # 1199
MATTRESS_Y0 = SLAT_Y0                    # -48  [was 29]
MATTRESS_Y1 = MATTRESS_Y0 + MATTRESS_W   # 752  [was 829] == SLAT_Y1
MATTRESS_Z1 = MATTRESS_Z0 + MATTRESS_H   # 1339

# ---------------------------------------------------------------------------
# SHARED LOWER DATUM  (hoisted - the ladder needs it before it is "its" section)
# ---------------------------------------------------------------------------
# The bench rail top is THE lower datum of the whole convertible section: it is
# the seat-height ledge, it is rung 1's top (D8), it is the bed-mode panel
# underside (D10) and it is the top of the stiffener battens (M4). It used to be
# declared down in LOWER CONVERTIBLE SECTION, which forced RUNG_TOPS[0] to
# repeat the literal 259 and left two numbers to keep in step by hand. It is
# hoisted here so every consumer derives from the one declaration.
BENCH_RAIL_TOP = 259                                # fixed by the doc (J9, J13)
BENCH_RAIL_BOTTOM = BENCH_RAIL_TOP - BENCH_RAIL_H   # 186

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
# side rail sitting on it (1065..1163); the highest fastener is still the M8 tie
# into the end beam (967..1065). Asserted further down (W2/W6 check).
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
#   FRONT POST (1700). Y restraints: the front bench rail segment laps its face
#   at 186..259, the end beam is fixed to its X-inner face at 967..1065 and the
#   front side rail at 1065..1163, then the two guard bands at 1414 and 1587.
#   Worst unbraced length is bench rail -> end beam, 967 - 259 = 708 mm, so
#   lambda = 68, lambda_rel = 1.16, k_c = 0.58 and N_c,Rd = 3528 * 0.58 * 12.92
#   = 26.4 kN against a corner reaction of well under 1.5 kN: utilisation ~0.05.
#   (The old 48x48 over the same 708 mm: lambda 51, k_c 0.75, 22.3 kN. The
#   thinner post is the STRONGER column, because 53% more area beats the loss in
#   radius of gyration.) The strong axis at the full 1700 is lambda = 60 - not
#   the governing case even unbraced.
#   BACK POST (1065). Take the Y restraints as the end beam alone (967..1065)
#   and the base as pinned: unbraced 967 mm, lambda = 93, k_c = 0.35, N_c,Rd =
#   15.8 kN against the corner reaction it carries in direct bearing off the
#   rail top - utilisation ~0.10. The back bench rail and the ledger butt and
#   screw to its X-inner face at 186..259 and 387..482, so the real unbraced
#   length is shorter than that; 967 is the conservative reading.
POST_HEIGHT = 1700                       # front posts + ladder uprights
BACK_POST_HEIGHT = RAIL_BOTTOM           # 1065, the rail underside (W6)
                                         # [was SLAT_Z1 = 1197, MATTRESS_Z1 1337]
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
assert WALL_Y == BACK_POST_Y0 == BACK_RAIL_Y0 == -48     # the mounting face

# W6: THE BACK RAIL BEARS ON THE POST TOPS. Post top == rail underside is the
# whole point of the round, so it is stated here as an identity and checked
# against the real parts in the validation section.
BACK_RAIL_ON_POST_Z = RAIL_BOTTOM        # 1065, post top == rail underside
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
END_BEAM_Y0 = BACK_POST_Y0                     # -48  [was -96, W6]
END_BEAM_Y1 = FRONT_POST_Y1                    # 788  [was 800, 906]
END_BEAM_LEN = END_BEAM_Y1 - END_BEAM_Y0       # 836  [was 848, 896, 1002]
END_BEAM_Z1 = RAIL_BOTTOM                      # 1065, flush with rail underside
END_BEAM_Z0 = END_BEAM_Z1 - RAIL_H             # 967
# D4/U2 ripple: the posts are 98 wide in X now, so the beams slide out to the new
# post inner faces X 98 / 1892 (they were at 48 / 1942 on a 48 mm post). The side
# rails run X 3..1987 and still cover both beams completely - 48 mm of full
# bearing on each, asserted in the validation block.
END_BEAM_X = [POST_W, WALL_SPAN - POST_W - RAIL_T]   # 98..146 and 1844..1892

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
#     edge distance in the direction the load acts (Z 994/1038 in a beam that
#     runs Z 967..1065). The perpendicular-to-grain loaded EDGE is what
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
#   In the ladder plane (X) the rungs brace the upright at 259 / 482 / 720 /
#   958, so the worst unbraced length there is the 259 mm floor-to-rung-1 and
#   lambda_x = 19 - irrelevant, and better than the 25 it was.
#   OUT OF PLANE (Y) is the one that moved, twice. v7: restrained at the bench
#   rail lap (top 259) and at the rail (1065), worst unbraced length 806 mm,
#   lambda_y = 58. v8/D13: the bench lap is gone, so the length runs floor to
#   rail, 1065 mm, and lambda_y = 77 on the 48 mm depth. v11/U2 turns the
#   section, so the same 1065 mm runs on i = 10.39: lambda_y = 102,
#   lambda_rel = 1.74, k_c = 0.29 and N_c,Rd = 1728 * 0.29 * 12.92 = 6.5 kN
#   against the ~1 kN a climber puts down an upright - utilisation ~0.15.
#   Ample, but this is now firmly a slenderness-governed member and the base is
#   still unrestrained in Y: the docs round must run the real EC5 6.3.2 check
#   and decide whether to add a floor-level tie back to the front corner posts.
#   (The panel's front U-brackets are that tie today - see M4/F1.)
LADDER_Y0 = FRONT_RAIL_Y1                # 752, outer face of the front rail
LADDER_Y1 = LADDER_Y0 + UPRIGHT_T        # 788, same plane as the front posts
LADDER_CLEAR = 320                       # clear width between the uprights
LADDER_CENTER_X = 995
LADDER_INNER_L = LADDER_CENTER_X - LADDER_CLEAR // 2          # 835  (FIXED)
LADDER_INNER_R = LADDER_CENTER_X + LADDER_CLEAR // 2          # 1155 (FIXED)
LADDER_LEFT_X = LADDER_INNER_L - UPRIGHT_W                    # 787 .. 835
LADDER_RIGHT_X = LADDER_INNER_R                               # 1155 .. 1203
MIN_LADDER_CLEAR = 300                   # EN 747 clear width between stiles

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
RUNG_D = TREAD_D                         # 73, tread depth (Y)
RUNG_Y1 = LADDER_Y1                      # 788, flush with the upright front
RUNG_Y0 = RUNG_Y1 - RUNG_D               # 715  [was 727]
RUNG_REST_LEDGE = LADDER_Y0 - RUNG_Y0    # 37, the bit behind the upright plane
# D8: an even climb. See the design-intent note - rung 1 shares its top with
# the bench rails (259) and rung 2 with the table-mode panel underside (482);
# 720 and 958 even out the rest of the way to the 1197 platform.
RUNG_TOPS = [BENCH_RAIL_TOP, 482, 720, 958]
MAX_CLIMB_STEP = 250             # comfort limit, rung 1 upwards
MAX_CLIMB_SPREAD = 20            # how uneven the climb proper may be

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
RUNG_BLOCK_T = BLOCK_T                   # 36 (X), stock thickness
RUNG_BLOCK_H = BLOCK_H                   # 48 (Z)
RUNG_BLOCK_LEN = RUNG_D                  # 73 (Y), same depth as the tread
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
GUARD_BAND_Z0 = [1414, 1587]             # [was 1412, 1585 - U1, +2]
MAX_GUARD_OPENING = 75           # EN 747 entrapment limit, above the mattress
MIN_GUARD_OVER_MATTRESS = 160    # EN 747 barrier height above the mattress
# D14: the guards hang inboard of the verticals now, so they overhang the
# mattress footprint by their own thickness. This is how much air has to be left
# between the mattress top and the underside of the lowest board for that
# overhang to be a non-event. It is the same 75 mm as the D6 opening - the band
# position sets both numbers at once - but it is a MINIMUM here, not a maximum:
# raise the bands and the clearance grows, lower them and the board starts to
# come down towards the mattress.
MIN_GUARD_INBOARD_CLEAR = 75
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
# they need is two full-height (1700) back corner posts, which is the OTHER half
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
BENCH_TOP = BENCH_RAIL_TOP + BENCH_SLAT_T      # 295, bench slat top / seat height
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
STUB_LEG_H = BENCH_RAIL_BOTTOM                 # 186, floor to bench rail underside
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
LEG_BEARING_AREA = LEG_W * LEG_T               # 3504 mm2  [was 2304, W3..U4]

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
# has to obey on every accessible edge is a BAND, not a maximum: under 12 mm a
# finger wedges, 12..25 mm it passes, and this design keeps every gap around
# the loose panel inside that window. 24 mm is the working number: it is inside
# the band with a millimetre of margin at the top, and it is exactly what the
# rear bracket flange needs to sit in (20 mm of flange + 2 mm of steel + 2 mm
# of clearance). The panel gets 28 mm narrower and the two numbers stay tied:
# widen the gap and the panel narrows with it.
PANEL_SIDE_GAP = 24                            # EN 747: inside the 12..25 band
EN_GAP_BAND = (12.0, 25.0)                     # accessible gaps must land here
PANEL_X0 = BENCH_LEN + PANEL_SIDE_GAP          # 669
PANEL_X1 = WALL_SPAN - BENCH_LEN - PANEL_SIDE_GAP   # 1321
PANEL_W = PANEL_X1 - PANEL_X0                  # 652  [was 680]
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
#   BED MODE    underside 259 = the bench rail tops = rung 1 top. It lands on
#               the back bench rail (680 x 48 = 32 640 mm2) and on rung 1
#               (320 x 25 = 8 000 mm2). Top 277 - see PANEL_BENCH_DIP.
#   TABLE MODE  underside 482 = the back ledger top = rung 2 top. It lands on
#               the ledger (680 x 21 = 14 280 mm2) and on rung 2 (320 x 25 =
#               8 000 mm2). Top 500.
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
#                           in BOTH modes (rung 1 at Z 259, rung 2 at Z 482,
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
PANEL_UNDER_BED = BENCH_RAIL_TOP               # 259, rests on the rails/rung 1
PANEL_TOP_BED = PANEL_UNDER_BED + PANEL_T      # 277
PANEL_UNDER_TABLE = RUNG_TOPS[1]               # 482, rests on rung 2/the ledger
PANEL_TOP_TABLE = PANEL_UNDER_TABLE + PANEL_T  # 500
# The whole move, in one number: the two seats are this far apart and the panel
# sub-assembly - sheet, battens, screws - is the same object at both of them.
PANEL_MODE_LIFT = PANEL_UNDER_TABLE - PANEL_UNDER_BED       # 223

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
#      rung ends are at X 835 / 1155 at BOTH heights (rung 1 at Z 259, rung 2
#      at Z 482), so one pair of battens guides the panel in both modes. The
#      pair lands at X 785..833 and 1157..1205, symmetric about the ladder /
#      panel centreline X 995 (centres 809 and 1181, i.e. +/- 186). Outboard
#      of the rung end there is nothing at any height in the batten's Y band
#      - the ladder uprights start at Y 752 - so the shaft is open top to
#      bottom and the assembly goes straight down it.
#   Y  rear: the back bench rail occupies Y -48..0 at Z 186..259, which is
#      exactly the bed-mode batten band, so Y0 = 0 (the back ledger at Y -48..0
#      is the same plane in table mode). Front: Y1 = PANEL_Y1 = 750, flush with
#      the panel's own front edge and the same 2 mm off the uprights the panel
#      already keeps. The last 35 mm of that - Y 715..750 - is the batten IN
#      the shaft, alongside the rung end.
#   Z  the batten TOP is the panel underside, so the battens hang BELOW it:
#      186..259 in bed mode, 409..482 in table mode. 186 is the bench rail
#      underside, which is the floor of the ladder-bay walking zone - the
#      battens sit at its ceiling and never enter it. Asserted below.
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
BATTEN_H = BENCH_RAIL_H                        # 73, batten depth (Z), on edge
BATTEN_Y0 = BACK_RAIL_Y1                       # 0, clear of the back rail/ledger
BATTEN_Y1 = PANEL_Y1                           # 750, the panel's own front edge
BATTEN_LEN = BATTEN_Y1 - BATTEN_Y0             # 750  [was 713]
BATTEN_X = [LADDER_INNER_L - PANEL_FIT - BATTEN_W,   # 785 .. 833
            LADDER_INNER_R + PANEL_FIT]              # 1157 .. 1205
BATTEN_Z0_BED = PANEL_UNDER_BED - BATTEN_H     # 186 == BENCH_RAIL_BOTTOM
BATTEN_Z0_TABLE = PANEL_UNDER_TABLE - BATTEN_H # 409
# THE SHAFT the batten runs in, and how much of it it uses. 48 mm of rung
# thickness in Z, 37 mm of rung rest ledge in Y (the bit of the rung that
# stands proud of the upright plane), and the batten occupies 35 of those
# 37 mm. Lifting the assembly clear of the rung end therefore takes RUNG_T of
# vertical travel, and that is the number the insertion sweep is measured
# against - it replaces the bracket leg it used to be measured against.
BATTEN_GUIDE_ENGAGE_Z = RUNG_T                 # 48, how far it has to lift
BATTEN_GUIDE_ENGAGE_Y = BATTEN_Y1 - RUNG_Y0    # 35, how deep into the shaft

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
# mode the cross batten is 223 mm higher and there is nothing beside it at all.
# A lock fitted there is therefore a bed-mode lock BY GEOMETRY, not by
# instruction, which is what an EN 747 conversion lock ought to be.
NOSE_Y1 = PANEL_Y1                             # 750, flush with the front edge
NOSE_Y0 = NOSE_Y1 - BATTEN_W                   # 702
NOSE_X = [(PANEL_X0, BATTEN_X[0]),             # 669 .. 785
          (BATTEN_X[1] + BATTEN_W, PANEL_X1)]  # 1205 .. 1321
NOSE_LEN = BATTEN_X[0] - PANEL_X0              # 116

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
#       ~4.7 kg of sheet plus ~2.4 kg of lekt, about 70 N. Picked up by one
#       corner with a factor 2 that is ~140 N, against 18 screws. ONE of them
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
#       nearly invisible. This panel is 652 wide, which is wider than shop
#       limtre furu goes, so it is 18 mm KRYSSFINER (see innkjopsliste): its
#       top face is a continuous rotary-cut veneer, and a 12 mm plug in it is
#       a disc of end grain in an unbroken face - twelve of them at 141 mm
#       pitch down the middle of the table. Near-invisible stops being
#       near-invisible on the material this part is actually made of.
PANEL_UPSCREW_LEN = 40                         # 5x40, the stock length
PANEL_UPSCREW_CBORE = 46                       # 12 mm hole, 46 mm up the batten
PANEL_UPSCREW_PASS = BATTEN_H - PANEL_UPSCREW_CBORE       # 27, batten left
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
#       greatest: tau = 1.5V/(b*h) = 1.5*1000/(116*36) = 0.36 MPa. The glue
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
# of the piece: at the 27 mm tip, tau = 1.5*1000/(48*27) = 1.16 MPa against
# f_v,d = 2.77, utilisation 0.42 - the highest number on the part, and it is
# the number that says do not take the tip any thinner.
NOSE_TIP_H = PANEL_UPSCREW_PASS                # 27, the up-screw's own seat
NOSE_ROOT_H = BATTEN_H                         # 73, full depth at the root
NOSE_TAPER_DEG = math.degrees(math.atan2(NOSE_ROOT_H - NOSE_TIP_H, NOSE_LEN))
# where the bending peaks along the taper, measured from the TIP
NOSE_CRIT_X = NOSE_TIP_H * NOSE_LEN / (NOSE_ROOT_H - NOSE_TIP_H)      # 68.1
NOSE_CRIT_H = NOSE_TIP_H * 2                                          # 54

# ---------------------------------------------------------------------------
# V4: WHERE A BED-MODE LOCK WOULD GO - AND WHY THERE IS NOT ONE
# ---------------------------------------------------------------------------
# THE DECISION, TAKEN: there is NO lock. It is an accepted deviation from
# EN 747 4.1.1 and the reasoning is written out in docs/ASSEMBLY.md, vedlegg B,
# avvik 4 - in one line: the mattress lies ON the panel and has to come off
# before the panel can lift, this is the LOWER bunk with a ~26 cm fall to the
# floor, and the panel is a ~9 kg unit whose guides take every lateral degree
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
# In bed mode both are in the Z band 186..259 and 24 mm apart across the side
# gap - two 48x73 end faces looking straight at each other. In table mode the
# cross batten is 223 mm higher and there is nothing beside it at all, so a
# lock fitted here is a BED-MODE lock by geometry and not by instruction: it
# cannot be left engaged in the wrong position, because in the wrong position
# it has nothing to engage. All three options in docs/preview/laasvalg.png act
# across that 24 mm; the geometry of all three stays valid whether or not one
# is ever fitted, which is exactly why the numbers below are still asserted.
LOCK_GAP = PANEL_SIDE_GAP                      # 24, the side gap itself

# The walking zone under the ladder bay: floor to the bench rail underside. The
# battens are not allowed into it in either mode.
WALK_ZONE_Z = (0, BENCH_RAIL_BOTTOM)           # 0 .. 186

# D10: the bed-mode panel top is deliberately 16 mm BELOW the bench tops. The
# fold-out seat cushions are what turn the three zones into one sleeping
# surface, and this is the recess they fold down into - a panel flush with the
# bench slats would leave the cushions standing proud of it instead.
PANEL_BENCH_DIP = BENCH_TOP - PANEL_TOP_BED    # 18  [was 16, U1]

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
LEDGER_BACK_T = BENCH_RAIL_T                   # 48 (Y)  [was BOARD_T = 21]
LEDGER_BACK_H = BENCH_RAIL_H                   # 73 (Z)  [was BOARD_W = 95]
LEDGER_BACK_Z1 = PANEL_UNDER_TABLE             # 482
LEDGER_BACK_Z0 = LEDGER_BACK_Z1 - LEDGER_BACK_H     # 409  [was 387]
LEDGER_BACK_Y0 = BACK_RAIL_Y0                  # -48 .. 0, on the wall plane

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
    if cut is not None:
        name, section, length = cut
        key = (name, section, round(length))
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
    if cut is not None:
        name, section, length = cut
        key = (name, section, round(length))
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
# W6: the back pair stands IN the back rail plane (Y -48..0) and stops at 1065,
# the rail underside, so the rail bears on it; the front pair is 1700 (guard
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
    parts.append(block(x0, END_BEAM_Y0, END_BEAM_Z0, RAIL_T, END_BEAM_LEN, RAIL_H,
                       f"End Beam {side}", "rails",
                       ("End beam", sec(RAIL_T, RAIL_H), END_BEAM_LEN)))
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
        parts.append(block(bx0, RUNG_Y0, top - RUNG_T - RUNG_BLOCK_H,
                           RUNG_BLOCK_T, RUNG_BLOCK_LEN, RUNG_BLOCK_H,
                           f"Rung Block {'Left' if j == 0 else 'Right'}_{i + 1}",
                           "boards",
                           ("Ladder rung block", sec(RUNG_BLOCK_T, RUNG_BLOCK_H),
                            RUNG_BLOCK_LEN)))
    parts.append(block(LADDER_INNER_L, RUNG_Y0, top - RUNG_T,
                       RUNG_LEN, RUNG_D, RUNG_T,
                       f"Ladder Rung_{i + 1}", "boards",
                       ("Ladder rung (tread)", sec(RUNG_T, RUNG_D), RUNG_LEN)))

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
# C5: 48x73 bench rails at Z 186..259, one per Y plane, each carried at its ends
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


def mode_parts(panel):
    """The WOOD. Every cut-list part, in one mode. Fasteners are NOT in here.

    This is the list the cut list, parts.tsv, the overlap check and the
    connectivity check all run over, and it must stay wood-only: a screw
    overlaps the two members it ties together on purpose, so it would fail the
    no-overlap assert on sight.
    """
    return parts + [mattress, panel] + PANEL_BATTENS[id(panel)]


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
    "guard":       r"Guard Rail Front (?:Left|Right)_\d+",
    "guard_host":  r"(?:Corner Post Front|Ladder Upright) (?:Left|Right)",
    "bed_slat":    r"Bed Slat_\d+",
    "bench_slat":  r"Bench Slat (?:Left|Right)_\d+",
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
    "guard": "rekkverksbord", "guard_host": "hjørnestolpe / stigevange",
    "bed_slat": "køyespile", "bench_slat": "benkespile",
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
          exempt=None, counterbore=0.0):
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
    """
    return dict(name=name, per=per, frm=frm, into=into, axis=axis, sign=sign,
                row=row, row_sign=row_sign, reach=reach, toe=toe,
                bracket=bracket, bears=bears, exempt=exempt,
                counterbore=counterbore)


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
#   TOE_SEAT_DEPTH   18 mm, measured ALONG THE SCREW, from the mouth of the
#                    pocket to its flat bottom - i.e. exactly how far the head
#                    is moved into the wood. It is one number for both joints
#                    (one setting on the depth stop), and it is set by the
#                    steeper of the two: the head is a disc of radius r_h in a
#                    plane square to the screw, so its highest point stands
#                    r_h*sin(deg) above the head centre measured along the face
#                    normal, and the centre is seat*cos(deg) below the face.
#                    Head fully under the wood therefore wants
#                    seat > r_h*tan(deg), which at J8-B's 65 deg and an 11.8 mm
#                    head is 12.7 mm. 18 - the same number as the bit, one
#                    thing to remember - leaves 2.3 mm of wood over the highest
#                    point of the head at J8-B and 4.9 at J10, and the assert
#                    below measures both on the solid rather than trusting this
#                    note.
# What it costs is length: 18 mm of the screw is spent in the pocket, so J8-B's
# 6x90 buries 72 mm of thread and J10's 5x70 buries 52. Both are re-checked by
# the ordinary tip-inside / tip-cover asserts, which know nothing about seats.
TOE_SEAT_D = 18.0                # Forstner diameter for the seat
TOE_SEAT_DEPTH = 18.0            # along the screw axis, mouth to flat bottom
TOE_SEAT_MIN_COVER = 1.0         # mm of wood over the highest point of the head
TOE_BENCH_POST = dict(face=1, face_sign=1, deg=65.0, back=34.0)
TOE_STUB_RAIL = dict(face=0, face_sign="inboard", deg=60.0, back=35.0)

# THE DRILL-GUIDE BLOCK - "vinkelkloss". A skew hole started freehand walks,
# and it walks worst exactly where these two are: near an end, in a face the
# bit meets at 25 or 30 degrees. The jig is an offcut of the bed's own 48x73
# with a ramp sawn on each end at the angle the drill has to keep - one end for
# each joint - clamped flat to the face with its ramp over the mark. It is NOT
# part of the bed, so it is not in `parts` and not in the cut list proper; it
# is a shop aid and it is listed as one (SHOP_AIDS below), cut in steg 0 on the
# mitre saw with the blade tilted.
#
#     ramp angle off the face = 90 - deg, i.e. the drill's own angle to the
#     face, because the bit lies ON the ramp.
TOE_JIG_LEN = 160                # one offcut, a ramp on each end
TOE_JIG_ANGLES = {"J8-B": 90.0 - TOE_BENCH_POST["deg"],     # 25 deg
                  "J10": 90.0 - TOE_STUB_RAIL["deg"]}       # 30 deg

# SHOP AIDS - things you CUT but do not BUILD IN. They are not parts of the
# bed, so they are not in `parts`, not in parts.tsv, not in CUT_LIST and not in
# the piece count; they are cut in steg 0 off the offcut pile and they belong
# in the manual because a jig you were never told to make is a jig you do not
# have when you need it.
SHOP_AIDS = [
    dict(key="vinkelkloss",
         name="Vinkelkloss (borjigg for skråskruene)",
         section=sec(BATTEN_W, BATTEN_H), length=TOE_JIG_LEN, qty=1,
         cut=(f"kappsag med bladet vippet, rampe målt FRA FLATEN: "
              f"{TOE_JIG_ANGLES['J8-B']:g}° i den ene enden (J8-B, dvs. "
              f"{TOE_BENCH_POST['deg']:g}° fra flatens normal) og "
              f"{TOE_JIG_ANGLES['J10']:g}° i den andre (J10, dvs. "
              f"{TOE_STUB_RAIL['deg']:g}°)"),
         use=("klemmes flatt mot flaten med rampa over merket; "
              f"⌀{TOE_SEAT_D:g} forstnerbor og deretter forboret hviler PÅ "
              f"rampa, så hullet får den vinkelen leddet er regnet på. "
              f"Brukes i J8-B og J10")),
]

JOINTS = [
    dict(id="J1", title="Endebjelke → hjørnestolpe", n=4,
         drill="⌀6 gjennom bjelken, ⌀4 i stolpen",
         side="Fra bjelkens utside, inn mot stolpen — helt inne i sengen, "
              "tilgjengelig hele veien. Disse to skruene er HELE festet: "
              "det står ingen kloss under bjelkeenden",
         contacts=[dict(a="post", b="beam", axis=0, drives=[
             drive("Treskrue 6×90 forsenket Torx", 2, frm="beam", row=2)])]),
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
         contacts=[dict(a="post_back", b="rail_back", axis=2, drives=[
             drive("Treskrue 6×120 forsenket Torx", 2, frm="rail_back")])]),
    # V5: same flip as J2. The stigevange's forside is in the front plane.
    dict(id="J3", title="Stigevange → fremre sidevange", n=2,
         drill="⌀6 gjennom sidevangen, ⌀4 i stigevangen",
         side="Fra sidevangens innside — inne fra sengen — gjennom vangen og "
              "inn i stigevangen. Stigevangens forside er urørt",
         contacts=[dict(a="upright", b="rail_front", axis=1, drives=[
             drive("Treskrue 6×80 forsenket Torx", 3, frm="rail_front")])]),
    dict(id="J4", title="Rungetrinn → stigekloss og stigevange "
                        "(per trinnende)", n=8,
         drill="⌀6 gjennom stigevangen inn i trinnenden; ⌀3,5 ned gjennom "
               "trinnet i klossen",
         side="6×120 fra utsiden av stigevangen; 5×60 ovenfra ned i klossen",
         contacts=[
             dict(a="rung", b="upright", axis=0, drives=[
                 drive("Treskrue 6×120 forsenket Torx", 1, frm="upright")]),
             dict(a="rung", b="rung_blk", axis=2, drives=[
                 drive("Treskrue 5×60 forsenket Torx", 1, frm="rung")])]),
    dict(id="J5", title="Stigekloss → stigevange", n=8,
         drill="⌀3,5 gjennom klossen, ⌀3 i vangen",
         side="Fra stigeåpningen, inn i vangens innside",
         contacts=[dict(a="upright", b="rung_blk", axis=0, drives=[
             drive("Treskrue 5×60 forsenket Torx", 1, frm="rung_blk")])]),
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
         drill="Først sete: ⌀18 forstner 18 mm ned LANGS skruens akse, med "
               "vinkelklossen som styring. Så ⌀6 skrått videre gjennom "
               "vangen og ⌀4 i stolpen — forbor hele veien, dette er en "
               "skråskrue nær en ende",
         side="Skrått fra vangens forside inn i stolpen, ut av et flatbunnet "
              "sete så hodet ligger helt under treet. Vangen ligger fast "
              "mellom de to stolpene, og disse to skruene er HELE festet i "
              "enden — det står ingen kloss under den",
         contacts=[dict(a="bench_back", b="post_back", axis=0, drives=[
             drive("Treskrue 6×90 forsenket Torx", 2, frm="bench_back",
                   toe=TOE_BENCH_POST,
                   exempt="skråskrue gjennom vangens forside nær enden")])]),
    dict(id="J10", title="Benkevange → stubbefot", n=4,
         drill="⌀3 i foten og i vangen. Skråskruen får først sete: ⌀18 "
               "forstner 18 mm ned langs skruens akse, med vinkelklossen som "
               "styring, så ⌀3,5 videre",
         side="Vinkelbeslaget sitter i hjørnet mellom fotens utside og "
              "vangens underside, med den ene fliken opp i vangen og den "
              "andre inn i foten; den ene 5×70 er en skråskrue nedenfra og "
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
             drive("Treskrue 5×70 forsenket Torx", 1, frm="stub",
                   toe=TOE_STUB_RAIL,
                   exempt="skråskrue nedenfra opp i vangen")])]),
    dict(id="J11", title="Benkespile → benkevange (per spileende)", n=20,
         drill="⌀3,5 gjennom spilen, forsenk hodet under flaten",
         side="Ovenfra, ned i benkevangen",
         contacts=[dict(a="bench_slat", b="bench_rail", axis=2, drives=[
             drive("Treskrue 5×60 forsenket Torx", 1, frm="bench_slat")])]),
    dict(id="J12", title="Bordbærelekt → bakre hjørnestolpe (endeskjøt)",
         n=2,
         drill="⌀3 i stolpen og i lekta — forboring er et krav: begge skruene "
               "står nær en ende, og lekta (48×73) tas i endeveden",
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
    # V3: NOTHING GOES THROUGH THE TOP OF THE PANEL. The panel is the table
    # top, and a table top with twelve screw heads - or twelve plugs - in it is
    # a table top with twelve marks in it. So the battens are glued to the
    # panel and the screws are driven UP from underneath, out of a counterbore,
    # and the sheet's factory face is never broken. See PANEL_UPSCREW below for
    # the three options and the numbers that picked this one.
    dict(id="J13a", title="Avstivningslekt → løs plate (limt, skrudd "
                          "nedenfra)", n=2,
         drill="⌀12 kontrabor 46 mm opp i lektas underside, ⌀3,5 videre "
               "gjennom resten av lekta. Ingenting gjennom platens overside",
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
         contacts=[dict(a="panel", b="nose", axis=2, drives=[
             drive("Treskrue 5×40 forsenket Torx", 3, frm="nose",
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

    def at(p):
        return tuple(a + b for a, b in zip(p, shift))

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
                         reach=reach, width=width,
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
                            face=(axis, face), through=None, into=target))
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
                            seat=seat, seat_d=TOE_SEAT_D,
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
                     reach=reach, width=b["width"], t=b["t"],
                     through=entry, into=target)]
    out = []
    for v in row_positions(lo, hi, dr["per"], d, what):
        p[row] = v
        out.append(dict(kind="screw", anchor=at(list(p)),
                        direction=_unit(axis, sign), length=length, d=d,
                        face=(axis, face), through=entry,
                        into=target, grips=target))
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
    for j, crow, c, pa, pb in inst:
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
        for s in offsets:
            for dr in crow["drives"]:
                for f in _place_drive(j, crow, c, pa, pb, dr, s):
                    f.update(jid=j["id"], name=dr["name"], drive=dr,
                             joint=j, crow=crow, contact=c, pa=pa, pb=pb)
                    specs.append(f)
    return specs


# The wall fixing is the one joint with nothing on the other side: it goes
# through the back rail and into the studs of a wall this model does not have.
# It is placed off the rail itself, spread along the length the way a builder
# spreads it across the studs he finds, and marked `wall` - the containment
# asserts and the mesh export both skip it, because everything past Y = -48 is
# in the wall.
def wall_fastener_specs():
    j = JOINT["J14"]
    name, count = j["fast"][0]
    d, length = 8.0, 100.0
    x0, x1 = back_rail.extents[0]
    y = back_rail.extents[1][1]
    z = sum(back_rail.extents[2]) / 2
    out = []
    for i in range(count):
        t = (i + 0.5) / count
        out.append(dict(kind="screw", anchor=(x0 + (x1 - x0) * t, y, z),
                        direction=(0.0, -1.0, 0.0), length=length, d=d,
                        through=back_rail, into=None, wall=True,
                        jid="J14", name=name, drive=None, joint=j,
                        crow=None, contact=None))
    return out


# ---------------------------------------------------------------------------
# BUILD THEM
# ---------------------------------------------------------------------------
# Bed mode is the one that gets fastened: the loose panel is the same part in
# both modes and carries the same steel, and the two joints it makes (J13b to
# the rung, J13c over the bench rail) are the bed-mode ones the drawings show.
_WOOD = [p for p in mode_parts(panel_bed) if p is not mattress]
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
        # the post runs 0..1065, printing a 994 mm "edge distance" off the
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


_SECTION_OF = {"J1": (RAIL_T, RAIL_H), "J2": (RAIL_T, RAIL_H),
               "J8": (BENCH_RAIL_T, BENCH_RAIL_H)}
SCREW_ROWS = screw_rows()

print("\n=== FESTEMIDLER ===")
print(f"OK  {len(FASTENER_SPECS)} festemidler plassert i "
      f"{len(JOINTS)} ledd, alle lagt ut etter (n-1)x4d + 2x3d")
for _j in JOINTS:
    _mine = [f for f in FASTENER_SPECS if f["jid"] == _j["id"]]
    _what = " + ".join(f"{q}x {n}" for n, q in _j["fast"])
    print(f"    {_j['id']:<5} n={_j['n']:<3} {len(_mine):>3} stk  {_what}")
for _name, _qty in sorted(HARDWARE_TOTAL.items(), key=lambda kv: -kv[1]):
    print(f"    {_qty:>4} x {_name}")



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
        _others[_mode] = [p for p in mode_parts(_panel) if p is not mattress]

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
                assert _under >= TOE_SEAT_MIN_COVER, (
                    f"{_label}: the highest point of the head stands "
                    f"{-_under:+.2f} mm past the face at {_surf:g} on axis "
                    f"{'XYZ'[_sax]} — the "
                    f"{_f['seat_d']:g} mm seat is {_f['seat']:g} mm deep and "
                    f"wants to leave {TOE_SEAT_MIN_COVER} mm of wood over it")
                TOE_SEAT_COVER.append((_label, _under))

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
        # pass by simply being 223 mm away from everything, which is the
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
    print(f"OK  V4 skråskruesete: alle {len(TOE_SEAT_COVER)} skråskruene "
          f"(J8-B ×4, J10 ×4) står i et flatbunnet ⌀{TOE_SEAT_D:g} sete boret "
          f"{TOE_SEAT_DEPTH:g} mm ned LANGS skruens egen akse. Minste tre "
          f"over hodets høyeste punkt: "
          f"{min(u for _l, u in TOE_SEAT_COVER):.2f} mm (krav "
          f"{TOE_SEAT_MIN_COVER:g}), største {max(u for _l, u in TOE_SEAT_COVER):.2f}"
          f" mm - målt på kroppene. Ingen TOE_HEAD_ALLOWANCE lenger: "
          f"skråskruene er like fullt inneholdt som alle andre")
else:
    print("(fasteners off - LOFTBED_FASTENERS=0)")


# ---------------------------------------------------------------------------
# THE PANEL'S OWN FASTENERS TRAVEL WITH THE PANEL
# ---------------------------------------------------------------------------
# THE BUG THIS KILLS, written down because it shipped: the fasteners are
# modelled ONCE, in bed mode, and `display_parts` used to hand that one list to
# both modes. The wood of the panel assembly is built per mode - panel_bed at
# Z 259, panel_table at Z 482 - but its screws were not, so in table mode the
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
for name, comp in (("bed mode", bed_mode), ("table mode", table_mode)):
    bb = comp.bounding_box()
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
assert OVERALL_DEPTH == 848 - POST_THIN, \
    f"U2/U3: re-sectioning the verticals 48 -> {POST_T} in Y should take " \
    f"exactly POST_THIN = {POST_THIN} mm off the 848 the bed was, not " \
    f"{848 - OVERALL_DEPTH}"
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
assert WALL_Y == BACK_RAIL_Y0 == -48 and BACK_POST_Y0 == WALL_Y, \
    f"W6: the wall plane is {WALL_Y}, want the back rail face {BACK_RAIL_Y0}"
print(f"OK  W1/W6/W7: WALL-SIDE BED - no back guard boards; the back face is the "
      f"flat mounting plane Y={WALL_Y} (was -96), the BACK RAIL FACE, made by "
      f"{len(on_wall)} coplanar parts - back side rail + 2 back posts tucked "
      f"into its plane + 2 end beams + 2 end-beam blocks + back bench rail + 2 "
      f"of its blocks + back ledger + all {len(bed_slats) + len(bench_slat_parts)} "
      f"slat ends - and nothing behind it. The fixing is screws through the back "
      f"rail into the studs, which also mid-support it")

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
# is 186).
# W2/W6 ripple: "floor to top" is no longer one height. The back pair stops at
# BACK_POST_HEIGHT = 1065 (the rail underside, which they carry) and the other
# four go on to 1700, so the membership test is the RAIL UNDERSIDE - the height
# at which a vertical is holding the platform up - not the literal 1700 and not
# the platform surface either, which the back pair no longer reaches.
VERTICAL_HEIGHTS = {
    "Corner Post Back": BACK_POST_HEIGHT,        # 1065, W6
    "Corner Post Front": POST_HEIGHT,            # 1700
    "Ladder Upright": POST_HEIGHT,               # 1700
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
# 2 x front corner post 36x98 x 1700, 2 x back corner post 36x98 x 1065 (U2;
# both were 48x48 up to v10), 2 x ladder upright 36x48 x 1700 (U2 turned them:
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
assert SLAT_Z1 - BACK_POST_HEIGHT == RAIL_H + BED_SLAT_T == 134, \
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
# 7: per post, the end beam, the back bench rail, the back table ledger, the
# back side rail and the outermost bench slat - x2, minus the three continuous
# members counted once.
# (Was 13 in v9, when the end slats butted the posts; 11 until V5 deleted the
# end-beam and bench-rail bearing blocks that hung on these two faces. After W6
# the upper slats are 98 mm above the post tops and touch nothing there, and
# the bench slats butt the post's X-inner face instead of clearing it in Y.)
assert len(back_post_neighbours) == 7, \
    f"W2/W6: the back posts touch {len(back_post_neighbours)} parts, expected " \
    f"7: {sorted(p.label for p in back_post_neighbours)}"
highest = max(back_post_neighbours, key=lambda p: p.extents[2][1])
assert highest is back_rail and highest.extents[2][1] == RAIL_TOP, \
    f"W6: the highest WOOD on a back post is '{highest.label}' at " \
    f"{highest.extents[2][1]}, expected the back side rail top {RAIL_TOP}"
# The M8 ties into the end beam (967..1065) are the highest fastener and they
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
      f"UNDERSIDE (was 1197, the platform top; 1337 before that), standing in "
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
assert front_top - wall_side_top == POST_HEIGHT - SLAT_Z1 == 501  # [was 503, 363]
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
assert LADDER_CLEAR >= MIN_LADDER_CLEAR, \
    f"D13: {LADDER_CLEAR} mm clear ladder is under the {MIN_LADDER_CLEAR} limit"
print(f"OK  D4: posts flush with the walls at X 0..{POST_W} / "
      f"{WALL_SPAN - POST_W}..{WALL_SPAN}; D13 ladder clear opening "
      f"{LADDER_CLEAR} mm (min {MIN_LADDER_CLEAR}) between X "
      f"{LADDER_INNER_L:.0f} and {LADDER_INNER_R:.0f}, upright outer faces "
      f"{up[0].extents[0][0]:.0f} / {up[1].extents[0][1]:.0f}, centred on "
      f"{LADDER_CENTER_X}")

# Fixed heights. Everything below the platform is untouched by D5/D6/D7; the
# platform stack itself is the thing that moved.
assert RAIL_BOTTOM == 1065 and RAIL_TOP == 1163
assert not any("Cleat" in p.label for p in parts), "D5: the slat cleats must be gone"
assert (SLAT_Z0, SLAT_Z1) == (1163, 1199), "D5/U1: slats not flush on top of the rails"
assert (MATTRESS_Z0, MATTRESS_Z1) == (1199, 1339)
assert (BENCH_RAIL_BOTTOM, BENCH_RAIL_TOP) == (186, 259)
assert BENCH_TOP == 295 and PANEL_TOP_BED == 277 and PANEL_UNDER_BED == 259
assert PANEL_TOP_TABLE == 500 and PANEL_UNDER_TABLE == 482
assert RUNG_TOPS == [259, 482, 720, 958] and POST_HEIGHT == 1700
assert BACK_POST_HEIGHT == 1065, "W6: the back posts must stop at the rail underside"
assert (LEDGER_BACK_Z0, LEDGER_BACK_Z1) == (409, 482), \
    "V2: the ledger is a 48x73 now, so its underside is 409 (was 387)"
assert STUB_LEG_H == 186, "W3: the stub legs keep their height"
print(f"OK  invariant heights held: rail underside {RAIL_BOTTOM}, rail top "
      f"{RAIL_TOP}, no cleats, slats {SLAT_Z0}..{SLAT_Z1} (flush on the rails, "
      f"U1: the {BED_SLAT_T} mm board took the platform 1197 -> {SLAT_Z1}), "
      f"mattress {MATTRESS_Z0}..{MATTRESS_Z1} (was 1197..1337), bench "
      f"{BENCH_RAIL_BOTTOM}/{BENCH_RAIL_TOP}/{BENCH_TOP} (seat was 293), ledger "
      f"{LEDGER_BACK_Z0}..{LEDGER_BACK_Z1}, rungs "
      + "/".join(str(t) for t in RUNG_TOPS)
      + f", panel {PANEL_UNDER_BED}..{PANEL_TOP_BED} (bed) / "
        f"{PANEL_UNDER_TABLE}..{PANEL_TOP_TABLE} (table), total {POST_HEIGHT} "
        f"at the front / {BACK_POST_HEIGHT} at the wall side (W6: the rail "
        f"underside, was 1197, 1337)")

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
assert BACK_POST_HEIGHT == 1065 and BACK_POST_HEIGHT == RAIL_BOTTOM, \
    f"W6: the back posts run 0..{BACK_POST_HEIGHT}, want 0..1065"
assert WALL_Y == -48 and WALL_Y == BACK_RAIL_Y0, \
    f"W7: the wall plane is {WALL_Y}, want the back rail face -48"
assert (END_BEAM_Y0, END_BEAM_Y1, END_BEAM_LEN) == (-48, 788, 836), \
    f"W6/U3: the end beams are Y {END_BEAM_Y0}..{END_BEAM_Y1} ({END_BEAM_LEN}), " \
    f"want -48..788 (836)"
assert END_BEAM_X == [POST_W, WALL_SPAN - POST_W - RAIL_T] == [98, 1844], \
    f"U2: the end beams are at X {END_BEAM_X}, want the new post inner faces " \
    f"[98, 1844] (98..146 and 1844..1892)"
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
assert (RUNG_Y0, RUNG_Y1) == (715, 788) and RUNG_D == 73, \
    f"U2: the rungs are Y {RUNG_Y0}..{RUNG_Y1}, want 715..788"
assert RUNG_REST_LEDGE == RUNG_D - UPRIGHT_T == 37, \
    f"U2: the rung rest ledge is {RUNG_REST_LEDGE}, want {RUNG_D} - " \
    f"{UPRIGHT_T} = 37"
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
assert SLAT_Y0 == WALL_Y, \
    f"W8: the slats start at Y {SLAT_Y0}, want the wall plane {WALL_Y}"
assert RUNG_REST_LEDGE == 37, \
    f"D12/U2: the rung rest ledge is {RUNG_REST_LEDGE} mm, want 37 (it was 25 " \
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
        assert bear >= RAIL_T - TOL, \
            f"'{rail.label}' only bears {bear:.1f} mm on '{beam.label}' in X"
print(f"OK  end beams {sec(RAIL_T, RAIL_H)} x {END_BEAM_LEN} at Z "
      f"{END_BEAM_Z0}..{RAIL_BOTTOM} carry both side rails "
      f"(full {RAIL_T} mm bearing in X, beams at X {END_BEAM_X[0]} / {END_BEAM_X[1]})")

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
BLOCKLESS_CORNERS = [
    ("J1", "endebjelkeende → hjørnestolpe", 1.0),
    ("J8", "fremre benkevangeende → fremre stolpe", 0.5),
    ("J8-B", "bakre benkevangeende → bakre stolpe", 0.5),
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
      f"{sec(RAIL_T, RAIL_H)} C24 - krav {MIN_EDGE} (3d)")

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
# There is only one position now, so both "extremes" are the drawn one and both
# gaps are 0. Kept as an explicit pair because it is the statement that the
# mattress is PINNED, not merely that it happens to be drawn tight.
gap_at_wall = MATTRESS_Y0 - MATTRESS_STOP_Y0                             # 0
gap_at_front = MATTRESS_STOP_Y1 - MATTRESS_Y1                            # 0
assert gap_at_wall == gap_at_front == MATTRESS_WANDER == 0, \
    f"W5: the mattress leaves {gap_at_wall} at the wall and {gap_at_front} at " \
    f"the front verticals; both must be 0"
assert WALL_MATTRESS_GAP == MATTRESS_Y0 - WALL_Y == 0, \
    f"W5: the mattress rear edge must BE the wall plane, not {WALL_MATTRESS_GAP}" \
    f" mm off it"
assert MATTRESS_Y1 == MATTRESS_STOP_Y1 == FRONT_POST_Y0, \
    "W5: the mattress front edge must be on the front stop"
# And the platform has to be under the mattress over the whole of it - trivially
# true now that the two are the same 800 mm band, but it is the assert that would
# catch the platform being pulled off the wall again.
assert SLAT_Y0 == WALL_Y == MATTRESS_Y0 and SLAT_Y1 == MATTRESS_Y1, \
    f"W5: the platform is Y {SLAT_Y0}..{SLAT_Y1} under a mattress at " \
    f"{MATTRESS_Y0}..{MATTRESS_Y1}"
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
    # full FACE contact over the whole lap and the whole board width, not an
    # edge kiss: the lap area is (X overlap) x (board width in Z).
    assert lap_post * GUARD_W >= (POST_W - THROUGH_X0) * GUARD_W
    assert lap_up * GUARD_W >= UPRIGHT_W * GUARD_W
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
MATTRESS_H_MIN = GUARD_BAND_Z0[0] - SLAT_Z1 - MAX_GUARD_OPENING
MATTRESS_H_MAX = GUARD_TOP - SLAT_Z1 - MIN_GUARD_OVER_MATTRESS
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
# The third opening closes against the FRONT post tops (1700). The back posts
# stop at 1197 (W2) and take no part in this check - on that side the "barrier"
# is a wall that runs to the ceiling.
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
# segment carried by the front posts, which are the ones that reach 1700.
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
# per end against the post's X-inner plane, 48 (Y) x 73 (Z) = 3504 mm2 of screwed
# contact. Measured against the real posts.
# U2: the face that end fixing lands on is 36 mm deep in Y now, not 48, so the
# contact is measured against the real post rather than assumed to be the
# member's whole end. Both members are 48 deep after V2, so both butt over 36
# of it - one number for the pair.
POST_TO_POST_ENDS = {
    "Bench Rail Back (continuous)": (back_bench_rails[0], BENCH_RAIL_H),
    "Table Ledger Back": (support_rail, LEDGER_BACK_H),
}
end_fixings = {}
for what, (member, height) in POST_TO_POST_ENDS.items():
    (rx0, rx1), (ry0, ry1), _ = member.extents
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
assert end_fixings["Bench Rail Back (continuous)"] == POST_T * BENCH_RAIL_H \
    == 2628, "U2: the back bench rail should butt 36 x 73 of post face"
# V2: the ledger is the bench rail's profile now, so it butts the same 36 x 73
# of post face the bench rail does - 2628 mm2 instead of the 21x95's 1995.
assert end_fixings["Table Ledger Back"] == POST_T * LEDGER_BACK_H == 2628, \
    "V2: the back ledger is 48 deep now, so 36 of it butts the post face"
assert BENCH_TOP == BENCH_RAIL_TOP + BENCH_SLAT_T == 295
# D10/U1: the cushion recess. The bench slat got 2 mm thicker and the panel did
# not (it is an 18 mm sheet on a rail top that has not moved), so the dip the
# fold-out cushions fold into grows 16 -> 18 mm. That is the right direction:
# the recess exists to swallow a cushion, and 18 mm of it is 18 mm.
assert PANEL_BENCH_DIP == 18 and PANEL_TOP_BED == BENCH_TOP - PANEL_BENCH_DIP, \
    "D10/U1: the bed-mode panel should sit 18 mm below the bench tops"
assert PANEL_BENCH_DIP == BENCH_SLAT_T - PANEL_T + (BENCH_RAIL_TOP -
                                                   PANEL_UNDER_BED), \
    "D10: the dip is the bench slat minus the panel, both off the same rail top"
print(f"OK  C5/W9/U2: back bench rail {sec(BENCH_RAIL_T, BENCH_RAIL_H)} x "
      f"{BETWEEN_POSTS_LEN} (was 1894, {THROUGH_LEN} before that) at X "
      f"{BETWEEN_POSTS_X0}..{BETWEEN_POSTS_X1}, Z {BENCH_RAIL_BOTTOM}.."
      f"{BENCH_RAIL_TOP} - butting both back posts over "
      f"{int(end_fixings['Bench Rail Back (continuous)'])} mm2 of their "
      f"{POST_T} mm X-inner faces (was 48 x 73 = 3504 on a 48 mm post) and "
      f"screwed to them (2 x 6x90 skråskruer per ende, J8-B - no bearing "
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
# out with it. They do occupy the top 73 mm of this box in bed mode (Z 186..259)
# by design: they hang under the panel, which is itself the ceiling of the bay
# at 259. What must stay empty for them is the WALKING zone, floor to Z 186 -
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

# D13: WALK-AROUND. There must be a real passage on each side of the ladder,
# between the sofa end and the upright outer face, clear from the floor up to
# the table-mode panel line (482) across the whole front zone.
#
# The clear width is measured against FIXED STRUCTURE (`parts`). The loose panel
# is handled separately below: it is the seat / table surface, it lies at 259 in
# bed mode and 482 in table mode, and it does bridge the passage at that height
# by design - what matters is that it never touches the floor level you actually
# stand and put your feet in, which is checked explicitly afterwards.
# D14 ripple: the front edge of the zone used to be the guard face (834). The
# guards went inboard, so it is the post plane now - the same 800 mm of front
# zone the check has always swept, minus the 34 mm that no longer exists.
PASSAGE_Y = (BACK_RAIL_Y1, FRONT_POST_Y1)            # 0 .. 800, front zone
PASSAGE_Z = (0, RUNG_TOPS[1])                        # 0 .. 482
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
#        walk-around, required clear from the floor to Z 482.
#   IN   the other stile, across the ladder opening, which EN 747 requires to
#        stay >= 300 mm clear. Tying the two stiles together adds nothing in Y
#        anyway - they move as one frame.
#   BACK the back bench rail, three quarters of a metre away across the D11
#        open bay, which is required clear to Z 259 - and above Z 186 the same
#        column is the panel's own insertion shaft.
#   FWD  NOTHING. There is no member in front of the ladder at all, and there
#        cannot be: U3 fixes the front face at Y = 788 and asserts Y 788..800
#        empty, and the overall depth is pinned at 836.
# So every direction out of the foot is either a protected void or the room,
# and the tie is not a detail this geometry can have as it stands. What it
# would cost to have one anyway is written up in vedlegg B.
FOOT_TIE_Z = (0, BENCH_RAIL_TOP)                 # 0..259, the foot proper


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
    assert b.extents[1] == (RUNG_Y0, RUNG_Y1)
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
    f"D8: the climb is uneven - steps {climb_steps}"
assert climb[-1] == SLAT_Z1, "the climb must end on the platform surface"
print(f"OK  D8: rung tops {'/'.join(str(t) for t in RUNG_TOPS)}; rises "
      + " + ".join(str(s) for s in steps)
      + f" mm from the floor to the {SLAT_Z1} platform - first rise "
      f"{first_rise} = bench rail top, then {min(climb_steps)}..{max(climb_steps)} "
      f"(limit {MAX_CLIMB_STEP}, spread {max(climb_steps) - min(climb_steps)} <= "
      f"{MAX_CLIMB_SPREAD})")

# D9: the front table ledger must be GONE and the back one's TOP must BE the
# table-mode panel underside - no hook step, nothing in between.
ledgers = [p for p in parts if p.label.startswith("Table Ledger")]
assert len(ledgers) == 1 and ledgers[0].label == "Table Ledger Back", \
    "D3: the front table ledger must be deleted"
assert not any("Front" in p.label and "Ledger" in p.label for p in parts)
assert ledgers[0].extents[2] == (LEDGER_BACK_Z0, LEDGER_BACK_Z1)
assert LEDGER_BACK_Z1 == PANEL_UNDER_TABLE == RUNG_TOPS[1], \
    "D9: the ledger top, rung 2 and the table-mode panel underside must coincide"
assert BENCH_RAIL_TOP == PANEL_UNDER_BED == RUNG_TOPS[0], \
    "D10: the bench rail tops, rung 1 and the bed-mode panel underside must coincide"
assert "HOOK_STEP" not in globals(), "D10: the hook step is supposed to be gone"
assert PANEL_X0 >= LADDER_INNER_L - 200 and PANEL_X1 <= LADDER_INNER_R + 200
print(f"OK  D9/W9: front table ledger deleted; back ledger "
      f"{sec(LEDGER_BACK_T, LEDGER_BACK_H)} x {BETWEEN_POSTS_LEN} "
      f"(was {THROUGH_LEN}, and 21x95 before V2) at X "
      f"{BETWEEN_POSTS_X0}..{BETWEEN_POSTS_X1}, Z {LEDGER_BACK_Z0}.."
      f"{LEDGER_BACK_Z1}, top level with rung 2, ends screwed to the back posts' "
      f"X-inner faces")

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
# Every named support is still far above the 5 000 mm2 floor.
MIN_BEARING = 5000               # mm2, per named support
PANEL_SUPPORTS = {
    "bed_mode": ("Ladder Rung_1", "Bench Rail Back (continuous)"),
    "table_mode": ("Ladder Rung_2", "Table Ledger Back"),
}
PANEL_RUNG_LEDGE = RUNG_REST_LEDGE - PANEL_FIT      # 35, the fit taken off
EXPECT_BEARING = {
    "bed_mode": {"Ladder Rung_1": RUNG_LEN * PANEL_RUNG_LEDGE,
                 "Bench Rail Back (continuous)": PANEL_W * BENCH_RAIL_T},
    "table_mode": {"Ladder Rung_2": RUNG_LEN * PANEL_RUNG_LEDGE,
                   "Table Ledger Back": PANEL_W * LEDGER_BACK_T},
}
for mode_name, panel in MODES.items():
    found = {p.label: bearing_area(panel, p) for p in parts
             if bearing_area(panel, p) > 0}
    for want in PANEL_SUPPORTS[mode_name]:
        assert want in found, \
            f"D10: the {mode_name} panel does not rest on '{want}' - it only " \
            f"lands on {sorted(found)}"
        assert found[want] >= MIN_BEARING, \
            f"D10: only {found[want]:.0f} mm2 of bearing on '{want}' in {mode_name}"
    # the front edge and the rear edge must BOTH be carried, or it tips
    assert any(a > 0 for lbl, a in found.items() if "Rung" in lbl), \
        f"D10: nothing carries the {mode_name} panel's front edge"
    assert any(a > 0 for lbl, a in found.items()
               if "Back" in lbl or "Ledger" in lbl), \
        f"D10: nothing carries the {mode_name} panel's rear edge"
    # D13: exactly two supports now, and exactly the areas the note computes.
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
assert PANEL_LEN == BENCH_SLAT_LEN - PANEL_FIT == PLATFORM_DEPTH - PANEL_FIT, \
    "D10/V2: the panel has to reach its rear bearing, less the front fit"
assert PANEL_Y0 == BENCH_SLAT_Y0 and PANEL_Y1 == LADDER_Y0 - PANEL_FIT
assert RUNG_Y1 == LADDER_Y1, "D10: the tread fronts must be flush with the uprights"
assert LADDER_Y0 - RUNG_Y0 == RUNG_D - UPRIGHT_T == RUNG_REST_LEDGE == 37, \
    "D10/U2: the rungs must reach 37 mm behind the upright plane to catch the " \
    "panel (25 while the upright was 48 deep - the tread did not change, the " \
    "upright did)"
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
assert BATTEN_LEN == BATTEN_Y1 - BATTEN_Y0 == 750
assert BATTEN_Y0 == BACK_RAIL_Y1, \
    "M4: the battens must stop at the back rail face, not run past it"
assert BATTEN_Y1 == PANEL_Y1, \
    "M4/V3: the battens must reach the panel's own front edge - the last " \
    "35 mm of them IS the guide, standing in the rung's rest-ledge shaft"
assert BATTEN_GUIDE_ENGAGE_Y == BATTEN_Y1 - RUNG_Y0 == 35 and \
    BATTEN_GUIDE_ENGAGE_Y < RUNG_REST_LEDGE, \
    f"M4/V3: the batten reaches {BATTEN_GUIDE_ENGAGE_Y} mm into a " \
    f"{RUNG_REST_LEDGE} mm shaft - past the ledge it would foul the uprights"
assert LEDGER_BACK_Y0 + LEDGER_BACK_T <= BATTEN_Y0, \
    "M4: the battens foul the back table ledger"
# V2/M5: the two front cross battens - the same stock, the same Z band, flush
# with the panel's front edge, and inside the panel outline in X.
assert NOSE_Y1 == PANEL_Y1 and NOSE_Y0 == NOSE_Y1 - BATTEN_W, \
    f"M5: the front cross battens are at Y {NOSE_Y0}..{NOSE_Y1}"
assert NOSE_X[0] == (PANEL_X0, BATTEN_X[0]) and \
    NOSE_X[1] == (BATTEN_X[1] + BATTEN_W, PANEL_X1), \
    "M5: each front cross batten must run from the panel edge to the M4 batten"
assert NOSE_LEN == 116 and NOSE_X[0][1] - NOSE_X[0][0] == NOSE_LEN == \
    NOSE_X[1][1] - NOSE_X[1][0], \
    f"M5: the two front cross battens are {NOSE_LEN} mm and equal"
# The corner they exist for, stated as the number it is: the panel's front edge
# outboard of the M4 batten, in bare 18 mm sheet. V3 shrank it 213 -> 116, and
# the note above is why that is not enough to delete them.
FRONT_CANTILEVER = NOSE_LEN                         # 116  [was 213]
assert FRONT_CANTILEVER == BATTEN_X[0] - PANEL_X0 == 116, FRONT_CANTILEVER
assert NOSE_Y0 <= RUNG_Y0, \
    "M5: a cross batten that starts behind the rung face would have to " \
    "thread past the rung, and the whole assembly goes straight down"
# V4: THE WEDGE, asked of the solid and of the screw seat.
assert NOSE_TIP_H == PANEL_UPSCREW_PASS, \
    "M5/V4: the wing's tip is the up-screw's own seat or it is a number " \
    "somebody liked - it has to be PANEL_UPSCREW_PASS"
_NOSE_TRAPEZOID = BATTEN_W * NOSE_LEN * (NOSE_ROOT_H + NOSE_TIP_H) / 2

# WHAT THE PANEL UNIT WEIGHS, off its own solids. It used to be a number in a
# comment - "4.7 kg of sheet plus 2.5 kg of batten" - and a number in a comment
# goes stale the moment the geometry moves, which is exactly what V4 did to it
# by planing 128 064 mm3 of wood off the two wings. Two densities and the real
# volumes instead. It matters in three places: the J13a up-screw check (the
# only load case those screws have is the unit being picked up by one corner),
# the lock decision in vedlegg B avvik 4, and what a parent is told to lift.
PLY_DENSITY = 500e-9             # kg/mm3, 18 mm gran kryssfiner
C24_DENSITY = 420e-9             # kg/mm3, rho_mean for C24
PANEL_UNIT_MASS = (abs(panel_bed.volume) * PLY_DENSITY
                   + sum(abs(b.volume) for b in battens_bed) * C24_DENSITY)
PANEL_UNIT_WEIGHT = PANEL_UNIT_MASS * 9.81                    # N
assert 6.0 < PANEL_UNIT_MASS < 8.5, (
    f"the panel unit is {PANEL_UNIT_MASS:.1f} kg - if that is right the "
    f"lifting argument in vedlegg B avvik 4 has to be re-read, and so has "
    f"the J13a up-screw case")
print(f"OK  plateenheten veier {PANEL_UNIT_MASS:.1f} kg "
      f"({PANEL_UNIT_WEIGHT:.0f} N) - "
      f"{abs(panel_bed.volume) * PLY_DENSITY:.1f} kg plate + "
      f"{sum(abs(b.volume) for b in battens_bed) * C24_DENSITY:.1f} kg lekt, "
      f"regnet av kroppene og ikke sitert. Løftet etter ett hjørne med "
      f"faktor 2 er {2 * PANEL_UNIT_WEIGHT:.0f} N mot 18 skruer i J13")
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
    assert _seen_wing_screws == 6, \
        f"M5/V4: {_seen_wing_screws} wing screws checked, want 6"
    _NOSE_CB = [round(_wing_height_at(_wings[_f["through"].label],
                                      _f["anchor"][0]) - PANEL_UPSCREW_PASS, 1)
                for _f in FASTENER_SPECS if _f["jid"] == "J13b"]
    print(f"OK  M5/V4 kile: begge vingene er skråkappet "
          f"{NOSE_ROOT_H} → {NOSE_TIP_H} mm over {NOSE_LEN} mm "
          f"({NOSE_TAPER_DEG:.1f}°), {_NOSE_TRAPEZOID:.0f} mm3 tre hver mot "
          f"{BATTEN_W * NOSE_LEN * BATTEN_H} som en hel kloss - "
          f"{100 * (1 - _NOSE_TRAPEZOID / (BATTEN_W * NOSE_LEN * BATTEN_H)):.0f}"
          f" % mindre synlig masse under forkanten. Tuppen ER skrueseten "
          f"({PANEL_UPSCREW_PASS} mm), så kontraboret bare grunner ut med "
          f"treet: {sorted(set(_NOSE_CB))} mm på de tre hullene. Verste "
          f"bøyesnitt ligger {NOSE_CRIT_X:.0f} mm fra tuppen (h = "
          f"{NOSE_CRIT_H:.0f} mm), ikke ved roten: "
          f"{6 * 1000 * NOSE_CRIT_X / (BATTEN_W * NOSE_CRIT_H ** 2):.2f} MPa "
          f"mot 16,6 = utnyttelse "
          f"{6 * 1000 * NOSE_CRIT_X / (BATTEN_W * NOSE_CRIT_H ** 2) / 16.6:.2f}"
          f"; skjær i tuppen "
          f"{1.5 * 1000 / (BATTEN_W * NOSE_TIP_H):.2f} MPa mot 2,77 = "
          f"{1.5 * 1000 / (BATTEN_W * NOSE_TIP_H) / 2.77:.2f}")
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
            if q is b or q is mattress:
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
    fixed = [p for p in parts if p is not mattress]
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
INSERT_CLEAR_MIN = 100           # mm of straight-up travel, both modes
INSERT_CLEAR = {}
INSERT_STOPPER = {}
for _mode in MODES:
    _run, _who = vertical_clear(_mode)
    INSERT_CLEAR[_mode] = _run
    INSERT_STOPPER[_mode] = _who
    assert _run >= INSERT_CLEAR_MIN, (
        f"V2 innsetting: the {_mode} assembly can only rise {_run:.0f} mm "
        f"before {_who} - it cannot be lifted clear of its own locators "
        f"(the guide battens engage {BATTEN_GUIDE_ENGAGE_Z:g} mm)")
    assert _run > BATTEN_GUIDE_ENGAGE_Z * 2, (
        f"V2 innsetting: {_run:.0f} mm of clear lift in {_mode} is less than "
        f"twice the guide batten's engagement - there is no room to aim it")
print(f"OK  V2 innsetting: the panel assembly - sheet, 4 lekter og "
      f"{sum(1 for f in FASTENER_SPECS if f['jid'].startswith('J13'))} skruer "
      f"- går rett ned i begge stillinger. Fri loddrett vei "
      f"{INSERT_CLEAR['bed_mode']:.0f} mm i sengestilling "
      f"({INSERT_STOPPER['bed_mode']}) og {INSERT_CLEAR['table_mode']:.0f} mm "
      f"i bordstilling ({INSERT_STOPPER['table_mode']}), mot "
      f"{BATTEN_GUIDE_ENGAGE_Z} mm som skal til for å løfte styrelektene fri "
      f"av trinnenden. Ingenting i veien for noen av delene på veien ned")

# 2 - EVERY DIRECTION HAS A BLOCKER, AND THE BLOCKER IS WOOD NOW.
# The five ways a seated panel can move without leaving its seat, and what
# stops each. This is read OFF THE MODEL, not asserted from the table: each
# entry measures a real clearance between two real solids. V3 deleted the four
# angle brackets, so what these asserts walk over is the BATTENS - and the
# thing they are measured against is the rung END GRAIN, in both modes,
# because rung 1 and rung 2 end at the same X.
def _guide_battens(mode):
    """[(side, batten, rung)] - the two guide battens and the rung end each
    one faces at THIS mode's seat height."""
    panel = MODES[mode]
    top = PANEL_UNDER_BED if mode == "bed_mode" else PANEL_UNDER_TABLE
    rung = next(p for p in parts
                if p.label.startswith("Ladder Rung_")
                and abs(p.extents[2][1] - top) < TOL)
    out = []
    for b in PANEL_BATTENS[id(panel)]:
        if abs((b.extents[1][1] - b.extents[1][0]) - BATTEN_LEN) > TOL:
            continue                       # a cross batten: never in a shaft
        out.append((_outboard(0, b), b, rung))
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
            # a guide that misses the rung in Y or Z guides nothing.
            for _j, _what in ((1, "Y"), (2, "Z")):
                _lap = (min(_b.extents[_j][1], _rung.extents[_j][1])
                        - max(_b.extents[_j][0], _rung.extents[_j][0]))
                _want = (BATTEN_GUIDE_ENGAGE_Y if _j == 1
                         else BATTEN_GUIDE_ENGAGE_Z)
                assert abs(_lap - _want) < TOL, (
                    f"V3 retning: in {_mode} the guide batten laps "
                    f"'{_rung.label}' by {_lap:.0f} mm in {_what}, want "
                    f"{_want}")
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
    assert PANEL_Y0 == WALL_Y, "V2 retning: the rear edge is not the wall plane"
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
          f"{BATTEN_GUIDE_ENGAGE_Y} mm tre mot trinnets endeved. Y- av "
          f"veggplanet, Y+ av stigevangene ({PANEL_FIT} mm), Z ned av tre "
          f"i hele platens bredde i begge stillinger - og Z OPP av "
          f"ingenting, med vilje: platen skal kunne løftes ut. Ikke ett "
          f"beslag igjen i mekanismen")

# 3 - THE EN 747 GAP BANDS, ON THE GAPS AROUND THE SEATED PANEL.
# The rule is a BAND, not a maximum, and it is the reason the panel got 28 mm
# narrower this round. A gap a child can reach is safe if a finger cannot
# enter it at all (up to 5 mm) or if it passes freely (12..25 mm); in between
# it wedges. Above 25 the check is no longer this one - it is the limb and
# head openings the guard rails are already held to at 60 and 75 mm.
EN_FINGER_FREE = 5.0             # a finger does not enter below this
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
for _what, _g in PANEL_GAPS.items():
    assert _g <= EN_FINGER_FREE + TOL or \
        EN_GAP_BAND[0] - TOL <= _g <= EN_GAP_BAND[1] + TOL, (
            f"EN 747: the gap '{_what}' is {_g:g} mm - a finger enters it and "
            f"wedges. It has to be at most {EN_FINGER_FREE:g} or between "
            f"{EN_GAP_BAND[0]:g} and {EN_GAP_BAND[1]:g}")
assert PANEL_X0 - BENCH_LEN == PANEL_SIDE_GAP == 24 and \
    (WALL_SPAN - BENCH_LEN) - PANEL_X1 == PANEL_SIDE_GAP, \
    "EN 747: the two side gaps must be equal and must be the declared one"
assert not (EN_GAP_BAND[0] <= 10 <= EN_GAP_BAND[1]), \
    "EN 747: 10 mm - the gap this design used to have - must NOT be legal"
print("OK  EN 747 klemfare: " + ", ".join(
    f"{_w.split(' (')[0]} {_g:g}" for _w, _g in PANEL_GAPS.items())
    + f" mm - hver enten under {EN_FINGER_FREE:g} (fingeren kommer ikke inn) "
      f"eller i båndet {EN_GAP_BAND[0]:g}..{EN_GAP_BAND[1]:g} (fingeren går "
      f"fritt). Sideklaringen var 10 mm, midt i klembåndet")

# D5: FLUSH TOP. No cleats anywhere; every slat lies on top of the rails and
# must bear on the FULL 48 mm width of BOTH of them, exactly like a bench slat.
assert SLAT_Z0 == RAIL_TOP, "slats do not sit on top of the rails"
assert MATTRESS_Z0 == SLAT_Z1, "mattress does not sit on the slats"
assert (SLAT_Y0, SLAT_Y1) == (BACK_RAIL_Y0, FRONT_RAIL_Y1)
assert SLAT_LEN == BENCH_SLAT_LEN == 800, \
    "D5: an upper slat is supposed to be the same piece as a bench slat"
assert (BED_SLAT_T, BED_SLAT_W) == (BENCH_SLAT_T, BENCH_SLAT_W) == (GUARD_T, GUARD_W)
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
assert SLAT_Z0 - BACK_POST_HEIGHT == RAIL_H, \
    f"W8: the slats start {SLAT_Z0 - BACK_POST_HEIGHT} mm above the back post " \
    f"tops, expected the rail height {RAIL_H}"
for s in bed_slats:
    for pe in BACK_POST_EXTENTS:
        inter = [min(a1, b1) - max(a0, b0)
                 for (a0, a1), (b0, b1) in zip(s.extents, pe)]
        assert min(inter) <= 0, \
            f"W8: '{s.label}' overlaps the back post at X {pe[0]} by {inter}"
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
assert MATTRESS_Y1 == SLAT_Y1, \
    f"D12: mattress front edge {MATTRESS_Y1} is not flush with the slat ends {SLAT_Y1}"
assert MATTRESS_Y0 == SLAT_Y0 == BACK_RAIL_Y0 == WALL_Y, \
    f"D12/W7: mattress rear edge {MATTRESS_Y0} is not on the wall plane {WALL_Y}"
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
#       covering the mattress band 1197..1337 in full;
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
    items = [p for p in mode_parts(panel) if p is not mattress]
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
    items = [p for p in mode_parts(panel) if p is not mattress]
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
# EXPORT
# ---------------------------------------------------------------------------
print("\n=== EXPORT ===")
os.makedirs(GROUP_DIR, exist_ok=True)
exports = []
group_files = []

for name, panel in MODES.items():
    comp = bed_mode if name == "bed_mode" else table_mode

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
        members = [p.moved(Y_UP) for p in display_parts(panel)
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
    y_up = make_compound(panel, Y_UP)
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
    sec(BOARD36_T, BOARD36_W),      # 36x98 - boards AND corner posts (U1/U2)
    sec(BLOCK_T, BLOCK_H),          # 36x48 - ladder uprights and every block
    sec(BENCH_RAIL_T, BENCH_RAIL_H),  # 48x73 - bench rails, rungs, battens,
                                      #         the four stub legs (U5) AND the
                                      #         back table ledger (V2)
    sec(RAIL_T, RAIL_H),            # 48x98 - side rails and end beams
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
assert len(TIMBER_PROFILES) == 4, \
    f"U1/U2/U5 aimed at 5 timber profiles and V2 took one out; " \
    f"this is {len(TIMBER_PROFILES)}"
assert by_section[sec(BOARD36_T, BOARD36_W)] == 32 and \
    max(by_metres, key=by_metres.get) == sec(BOARD36_T, BOARD36_W), \
    "U1/U2: 36x98 must be both the most numerous and the longest profile"
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
      f"{SLAT_LEN} mm long (was 906) and the end beams {END_BEAM_LEN} mm (was "
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
      f"and their blocks, the back bench rail and its blocks, the ledger and all "
      f"{SLAT_COUNT + BENCH_SLAT_COUNT * len(BENCH_X)} slat ends, all coplanar - "
      f"and the mattress gap is {MAX_MATTRESS_GAP} mm (W5), against the "
      f"{MAX_GUARD_OPENING} mm EN 747 entrapment limit. The two deleted boards were "
      f"{sec(GUARD_T, GUARD_W)} x {THROUGH_LEN}; putting them and two full-height "
      f"({POST_HEIGHT}) back posts back is the retrofit if a freestanding "
      f"version is ever wanted, but after W6 it also means moving the posts back "
      f"out into a layer of their own - flagged for the docs round.")
print(f"Note (W6): the two BACK corner posts stand IN the back rail plane "
      f"(Y {BACK_POST_Y0}..{BACK_POST_Y1}, was -96..-48) and are cut to "
      f"{BACK_POST_HEIGHT} mm (was 1197, 1337) - the RAIL UNDERSIDE. The back "
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
      f"is the WHOLE end fixing: 2 x 6x90 skew screws per end, 4.0 kN in shear "
      f"against 0.5. The bench slats are re-pitched to start at the post inner face: "
      f"X {BENCH_SLAT_X_START}..{BENCH_LEN}, pitch {BENCH_SLAT_PITCH:g} (124.75 "
      f"in v10, 137.5 before that), gap {BENCH_SLAT_PITCH - BENCH_SLAT_W:g} mm "
      f"(26.75, 39.5) - same five pieces per bench, closer together each time "
      f"the post got wider.")
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
      f"The {sec(RUNG_BLOCK_T, RUNG_BLOCK_H)}x{RUNG_BLOCK_LEN} rung blocks are "
      f"unchanged - their 36 mm is stock thickness, not upright width.")
print(f"Note (U1): the board profile is {sec(BOARD36_T, BOARD36_W)}, not 34x98. "
      f"34x98 was a drawing dimension; {sec(BOARD36_T, BOARD36_W)} is the shelf "
      f"item. The board is 2 mm thicker and nothing else about it changes - same "
      f"{BOARD36_W} mm width, same lengths, same pieces - but the 2 mm shows up "
      f"in every stack a board is IN: platform top 1197 -> {SLAT_Z1}, mattress "
      f"{MATTRESS_Z0}..{MATTRESS_Z1}, bench top 293 -> {BENCH_TOP}, cushion "
      f"recess under the bed-mode panel 16 -> {PANEL_BENCH_DIP} mm, guard bands "
      f"up 2 to {GUARD_BAND_Z0[0]}..{GUARD_BAND_Z0[0] + GUARD_W} and "
      f"{GUARD_BAND_Z0[1]}..{GUARD_BAND_Z0[1] + GUARD_W}. The EN 747 openings "
      f"above the mattress are unchanged at 75 / 75 and the third closes "
      f"against the fixed {POST_HEIGHT} post tops: 17 -> "
      f"{POST_HEIGHT - (GUARD_BAND_Z0[1] + GUARD_W)} mm.")
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
      f"every joint into a corner post switches to the 6x90 pre-drilled screw "
      f"pattern the ladder uprights already use (J3): 6 mm wants 3d = 18, which "
      f"is exactly what a {POST_T} mm face gives, and 6x90 through a {RAIL_T} mm "
      f"rail leaves 42 mm in the post. Stacked along the post grain as the ties "
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
# PARTS SNAPSHOT
# ---------------------------------------------------------------------------
# parts.tsv is the tracked regression snapshot: every part's label, colour group
# and bounding box, sorted by label. Both panel positions are in it, told apart
# by the "(bed mode)" / "(table mode)" suffix on the label. It is the one
# generated file that IS committed - a diff on it is the diff on the model.
snapshot = parts + [mattress, panel_bed, panel_table] + battens_bed + battens_table
snap_path = os.path.join(OUT_DIR, "parts.tsv")
with open(snap_path, "w", encoding="utf-8") as fh:
    fh.write("label\tgroup\tx0\tx1\ty0\ty1\tz0\tz1\n")
    for p in sorted(snapshot, key=lambda q: q.label):
        (x0, x1), (y0, y1), (z0, z1) = p.extents
        fh.write(f"{p.label}\t{p.group}\t" + "\t".join(
            f"{v:g}" for v in (x0, x1, y0, y1, z0, z1)) + "\n")
print(f"\nwrote {snap_path} ({len(snapshot)} parts, both panel modes)")
