import sys
import os
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# these results were produced by original Kociemba's Java implementation
javares = [
    ("BBURUDBFUFFFRRFUUFLULUFUDLRRDBBDBDBLUDDFLLRRBRLLLBRDDF",
     "B U' L' D' R' D' L2 D' L F' L' D F2 R2 U R2 B2 U2 L2 F2 D' "),

    ("FDLUUURLFLBDFRRDLBBBUBFLDDLFBBUDUBRLURDFLRUFRFLRFBDUDR",
     "U F' L2 U F' L2 F L2 F2 D L' F' U2 B2 D F2 D' R2 L2 D F2 U' "),

    ("UDRFULDRBLDUBRDUFBFBDRFDFURLBBLDRDURLLRULUFBUFRBFBFDLL",
     "F U2 D2 L' F2 D' B R L2 U F U F2 D2 B2 D R2 U2 F2 L2 B2 "),

    ("LRLLURRLBDUULRFUFLFDRUFBRBLDUFDDRRBDDFURLLBFFBDBUBBFDU",
     "B2 D' R2 F U R F' D2 L' B D F2 R2 L2 U' B2 D2 B2 U B2 "),

    ("UUULULFLFDUBDRRDBBUFLFFLBRRLDFFDDBUUFBRRLDRUDLBLFBBRRD",
     "U2 F' D F U F' U F2 R' F R' D2 R2 F2 U2 D B2 U2 L2 F2 "),

    ("LRRFUUBDLFBBLRDLLRUFDLFURLFBBUBDDDDUDULRLFRRDUUBRBFFBF",
     "R' B' D' R' B' L F2 U' D F' R2 L2 U' R2 F2 U R2 U B2 D' "),

    ("FBRDULFBRFBBRRRDLBRRUDFUUDFLBLFDUBFDLLDLLFRRBUUUDBFLUD",
     "U F R' D' R' U2 L D B' R L' U' B2 L2 U2 D2 B2 R2 D L2 B2 "),

    ("FLBUULFFLFDURRDBUBUUDDFFBRDDBLRDRFLLRLRULFUDRRBDBBBUFL",
     "U2 D B' U2 R' D2 L2 D R2 L B' U' L2 D L2 D F2 L2 B2 U' "),

    ("UBLLURBDLDDFRRLRFLDFBLFURFFFLDBDULBUBDRRLBDDUUURUBFBRF",
     "U' R2 F U2 R' L' F' L U D' R' U' R2 B2 L2 B2 L2 U2 R2 D' F2 "),

    ("UDLFUBLRFRDDLRFDBDBBDDFUUUBFRRLDUFFLBLUFLRRBLFLRUBDBRU",
     "U R' L F L' U' F' D R F' L' B2 U L2 B2 D L2 U2 R2 B2 D "),

    ("URBLUBDDBURDLRDLDBFBLLFFULDBBFUDFLRRRURBLDFFRLUFRBUDFU",
     "U2 R2 F' R B' D2 B L' B U' R2 B L2 F2 U2 F2 U' R2 D' L2 D R2 "),

    ("BLBDUULUDBLRDRFLBUUBLRFFURDLDFRDRRUFRBFLLUFFBDDULBBRFD",
     "U2 D2 B' D' F B L2 F2 L D2 L' U F2 U L2 D L2 U2 L2 D F2 "),

    ("ULFUUURRURLLLRRUBLDFFLFFBDRURBRDDDFBFBFFLDBBLDBLUBDDUR",
     "U2 B2 L2 B' D R U2 B2 L' U D2 F' U F2 L2 U2 D' R2 F2 U2 D' F2 "),

    ("LUFBUUUDDLLRDRRDDLBFFFFRUDBLLRRDBRBFDURFLRFUBUFBBBLULD",
     "D' L B2 U' F' B U B' R2 D2 R' B2 L2 U R2 U B2 R2 U' F2 D2 "),

    ("UDDBURDDBUFLFRLFDFRRLRFLUBRFDUBDFRFLBLBRLUFULBLRUBBDUD",
     "U2 B' U' B' R' F2 U' L' F' D B U F2 D2 F2 D F2 R2 U2 F2 D' "),

    ("UUBUUBUDBDRLFRFDUDBBRBFRFBRUUFDDLLDFFRRDLLBRRUFLLBFLLD",
     "U2 R' B2 U' F2 D B R F2 R U2 B2 U2 R2 U' F2 U2 R2 D' "),

    ("BDLRULLRRDFFBRLDRLBFFFFUUDBBRRLDURDDLBULLUUBRUBDUBDFFF",
     "F2 D' L2 U B' D B L F' B U' L2 D2 L2 B2 U R2 F2 U F2 "),

    ("LFRUULBBDBFBDRBLFRDDLLFLFRDRBFDDUBUUURRFLBLRDURFUBDFLU",
     "R' D' F' R U' L2 D2 R D L' D' F2 D' R2 U' R2 F2 B2 L2 U2 "),

    ("UBBRUDBLFRBRRRUFBBLFDDFFFULUFDDDLBLUFUDBLRLFRDULLBRRDU",
     "R' U B R U' R D' R2 L' F' R' F2 R2 U L2 D' B2 U2 L2 D' "),

    ("FRRUUFURDBLFRRFFLUBDLRFBLFUFULLDDBBBULRDLURBDDFRDBBLUD",
     "U R2 U F R' B' R F2 D F' L' D' R2 D B2 D' L2 B2 D R2 L2 "),

    ("ULDFUBBRRBDLFRBFFLUUDBFLRFDUDRLDUFUDRRLDLUUDBBBFRBRFLL",
     "F' B' L' U D B U2 F' B' D2 R' B2 U L2 D' F2 R2 D2 R2 U R2 "),

    ("ULLLURFBBDUBBRUBLFURRDFDRFUDRRFDBUULLURRLLLDFDFBBBDDFF",
     "U' F2 D2 B2 R2 U B R B U L' B' U B2 D B2 R2 D L2 U D2 "),

    ("BDBDURFFRDFDRRLUBLLLFBFURFBBULDDURLDRFURLRUBDLLUUBDFBF",
     "U2 B2 U' F' D' R2 U F2 D' L' B R2 B2 U' B2 U' B2 D' B2 R2 U' "),

    ("DRUUUDDBRULLBRBFFLLLBFFDBURLFUUDLRRURRFFLDFLDFDBUBRBBD",
     "D F R L B2 L' B U F' D' R U B2 U F2 U B2 U2 F2 U' L2 "),

    ("BDLLURUFRDBDRRRDFURLFLFUBFLRDBLDUBBLDDFFLBLUUFBRDBRFUU",
     "L' D R' U' B D F D F2 B' R B2 U' L2 U' F2 U D F2 R2 D2 "),

    ("RRRUURUUBDDBFRBFLURLRFFRLULDBDLDBLLLDFFULDUDBUBFDBRFFB",
     "U D2 R' F' R' U' B R' U' L F2 B2 U2 B2 D' F2 D R2 F2 D2 "),

    ("LFRLUUBBLBFUDRRUUFDDUDFFULLBUFLDBLFDFDRBLRBBRFRDUBRRLD",
     "F2 R U' F D2 B D B' L U2 R U F2 U2 R2 U2 R2 U' B2 D' "),

    ("FRRBUBDDURLBDRDLUDRLFLFBLBFDUUFDRLUFRRBRLFUUBUDDFBFLLB",
     "U2 D F' B' R' D' L B' R B R L2 D2 L2 F2 U B2 R2 B2 D2 F2 "),

    ("DBUFUFDFUBLLLRURUBLRRDFBFLDUUBFDRDDLFUFBLLLDRFDRBBRURB",
     "F' B' U' B2 D' F L U' B R' D2 L2 U2 F2 D B2 U' F2 U2 L2 "),

    ("BFRFUBBLBLRFDRBDUUUBDFFRLFFULLDDRFDRDULLLRRLFDDRUBUBBU",
     "L F2 R F' U2 R F' L F R U F2 D2 R2 U R2 L2 B2 D2 F2 "),

    ("BFDDURFBRDBLURLBUUDLFRFBDRURURLDLFFFUBLFLDUFBBRLDBDRUL",
     "L2 U R2 B L' F L' F' R' L F R2 U2 R2 U F2 U F2 D R2 D2 "),

    ("LRBUULRDRDBLLRBDDUFRFDFURLLBFBUDBBFLFBUDLFURDUFDRBLFUR",
     "R' B' D' R2 L B' L D L' B' U2 L2 D2 R2 B2 U' L2 D' F2 B2 "),

    ("RBBDUBBRRFLDFRFFRRDUUFFUDFULLLLDBBLBDBRDLRLUFLUFDBRUDU",
     "U2 F2 U' D2 F U' R B' U L F B2 U D B2 R2 U2 B2 D' F2 "),

    ("FRBUURUDBLBRDRLDFDRBDDFLUFFLULDDLBLRLBFFLRUFBDUUUBRFBR",
     "D B' U' D' F' U2 F' R F D2 F B2 U D2 F2 R2 D2 L2 F2 D' B2 "),

    ("FLURURDBRBDBBRUUUUFLDFFULUFFLRDDRLBRLFRFLLBBDLDUFBDBRD",
     "F' U' F2 D2 F2 L' B' R2 U' R F U B2 D L2 D' F2 R2 D L2 U2 "),

    ("BULRUULFRDBDDRLUDRULFFFBLUBDRLFDLURBDBFLLDFRBFFRUBBUDR",
     "U' F2 R' D2 L2 U2 F' B' R' F' B2 U2 D L2 F2 L2 D' F2 U2 F2 "),

    ("FFRRULFBDRFBURLFBUDLBRFFDBRBUUDDDLRLRULRLDULLUDDUBFFBB",
     "U F D' B' U D' F L2 U R F' R2 F2 U' R2 F2 D' R2 U D' B2 "),

    ("DUFBUDBRDBRUFRURRBDFLLFDDLBLFULDURBLFDRDLBUUFLBRFBLURF",
     "U L2 B D' L' U B' R2 L2 D' R F2 B2 R2 U2 B2 U' D2 F2 B2 R2 "),

    ("DRRUURBRURUBDRLUBFDBFBFBLFLDRFFDULLDLFRDLLUDBUDFUBLRFB",
     "F2 B D2 R B' U2 B2 D2 F' L B2 R2 F2 L2 U' L2 U' R2 B2 U "),

    ("BRLFUDLDRFLUFRUFFLFBURFRUUDFBRUDDRRBRLDLLBDLLBUUFBBDDB",
     "F2 D L F' B' L' F2 D F' U' R U F2 L2 F2 L2 F2 U2 L2 U' R2 "),

    ("UULFUFDLRFDBBRDBLFLFULFUDDURBRRDDURDFUFLLBBFBDRLRBURBL",
     "F' R U B2 D B U2 R' L' F' L' D' F2 R2 U F2 L2 U2 B2 U B2 "),

    ("DUDUUUDBUFRFRRBRDUBLLUFDUBFBDDFDLUFFRBLFLFBRRLLBRBDRLL",
     "B2 L U B' R' F2 B D2 R2 U2 R' U' R2 D' R2 D' R2 U B2 U' R2 "),

    ("LDRLUDRLFURBRRRRDDBBRFFUUBFLUDUDLLBFUFDFLUBLBUBFFBDLRD",
     "D F2 R' L2 D' B2 R' D' L B U' F2 R2 B2 R2 F2 U B2 U D "),

    ("FUBUUFLBLURRDRFFUDDUFBFRUBDBLRRDLBFFURBLLDLBRDFRLBDLDU",
     "F R' U L B' U' R2 L F D' F' D L2 D B2 U' B2 U2 R2 B2 L2 "),

    ("DFRBURUDDLBDRRFUDULLFLFUULFFBRRDRFBRBDBFLUDFLBULDBLBUR",
     "U F2 R B' U L' U2 L' U' B2 L F U' R2 D2 F2 R2 D2 B2 D B2 U' "),

    ("RLRUURDLFUFDBRLFRBLFRFFDDLUFULRDUDFLUBFRLULBRBDBBBDUDB",
     "U2 F2 D' F' L' F' B' U B' R' L2 B' U' F2 L2 D L2 U' F2 U2 L2 U2 "),

    ("BBURULRUULFLBRRBFBDFBFFDFRDUULUDRDDUDBFLLDFBRFLRDBURLL",
     "U F D L2 U2 R' L U2 B2 R B' D' R2 D' F2 B2 D F2 D L2 D2 "),

    ("LBLLUBUFUBRUURFDLRRLRDFLDFLFRBRDDLBDFBFRLFFDRBUDUBUBDU",
     "U L' D2 B U B D2 F R B U2 R' D' R2 U L2 D R2 D2 R2 D2 F2 "),

    ("FUFBUBURDFLRDRFBUFLDRFFLBDDDBLFDLURLLUBFLURDRURULBRDBB",
     "B' R L F U' B' U L U R' B U L2 U2 L2 F2 U' F2 L2 B2 U2 "),

    ("RURFUDDDFLBBFRULUBFFUDFLDLDRBFBDLBDLFRRULRDRBURUBBFULL",
     "U' D' R B2 U R2 F2 R' F' L' U' F2 B2 R2 D B2 U2 R2 U2 R2 "),

    ("DBRDULBFBUDUDRRULLDRLLFRLBRFUBUDUDDFBFRBLFRFDFLLUBRUBF",
     "L' U R2 L F2 D2 B' U' L U2 R2 U D' R2 D' F2 R2 F2 "),

    ("URBLUBFDUBRRLRFLULRLRBFFLDDBFFLDRFFBRBDBLUUUUDDFRBDDUL",
     "U' R L' F' R' U B R2 U B2 R' F2 R2 B2 U2 D R2 U D2 F2 U2 "),

    ("BUULURRDFRURFRBUFUBLDDFLFBFDRRBDRUULLBDRLFBULBFDDBDFLL",
     "R D L' U' R2 B' L2 B2 U F' D' R U2 D' F2 R2 F2 D' F2 U L2 D "),

    ("FURBUDLRRUBDFRLBDFBUBFFRUDDRRLDDFULLRUUBLULLFBLDBBRDFF",
     "R B' U' F' B2 L2 D2 R' U2 F' L D L2 U2 D' F2 L2 U R2 B2 R2 "),

    ("LLRDUBUBBURBBRBLRRRLLLFUBFDDRFFDUULFDFFDLULURUDBDBRDFF",
     "R2 L2 U' B' U2 L' B' R L' D2 B D F2 B2 L2 U' F2 D B2 U "),

    ("FDRUUBBBLDRBDRLFFFDUBLFRBURURUFDRFFUDLRFLBDLLUBLDBDLUR",
     "U D2 B' U' L' U' F U' B R' D2 L D' B2 U2 R2 D R2 L2 B2 "),

    ("FBBDULLFRUBRLRLDFUDRBBFFUURLLFUDDDBLURBFLRFRBDURDBUFDL",
     "U R' D L' U2 D L U2 L' D2 F' R D' L2 U2 R2 D' F2 R2 D' F2 D2 "),

    ("LLBDURRDURBDLRLRULBBFBFDDBBFUUFDRLFFBRDFLLDDRLUUFBRUUF",
     "U2 L' U2 B' R L2 U R' F2 R' B D R2 U2 D R2 F2 D R2 L2 F2 "),

    ("LFFDUBLRDLLDURLBDFDUFLFFFDUUBRRDRDBUBLBRLUBBRRDUFBFLUR",
     "D2 B2 L' F R' L' B' L2 F2 D' R' U2 B2 D2 B2 D L2 U F2 D' F2 "),

    ("FBUDUBBRBUURLRRUFLDBLLFDRFFDLRFDRFUBDBRRLUUDFBLLUBDDFL",
     "R2 U R F' U R2 D2 B' R' B' R' U2 F2 D F2 U F2 D2 L2 B2 D' "),

    ("ULBFURBDBDDDFRRBFFUBRLFUFRURBRUDDDLURRLLLFFBDLDFUBULBL",
     "F2 L U' R' B2 L' D B2 L B' D' B2 U B2 L2 U B2 L2 D2 R2 "),

    ("DUBBUFLFFLRLDRBBLRDUUDFLLRRFBDDDURRUFLBFLRBFDUBRDBLFUU",
     "D' F' D' L' F2 D F D2 R' L2 D2 R2 D B2 D B2 L2 U R2 "),

    ("BRDFUUUUULBFDRDDDFRLBUFRLBBUDRFDLBLDRRFBLFDLFLUUFBRRBL",
     "L' U R' F B2 D F R B R L2 D R2 U2 F2 R2 B2 R2 U R2 "),

    ("DBRLUFFUBDLFBRFLBLLFRFFUBLBRUDDDDFUULDUBLRRRUDLFDBRBRU",
     "R2 B2 R' L' F2 R2 B' D L U B D B2 R2 D' R2 D B2 D2 F2 "),

    ("LLURULDUDLBLURBBRFRFFRFLFRURBRFDDBBRDFBFLULDDFDBUBLUDU",
     "U F D' R' B' U R' F' D' F U2 L B2 U2 D L2 F2 L2 U F2 L2 U "),

    ("UFLRULBLUBUBBRFRDFDFRBFLFUFLRDDDRBBLRFRBLULLUDDFUBDDRU",
     "U R L' D2 B' L F2 U F L2 U2 L D' R2 D2 R2 B2 U' L2 F2 D' L2 "),

    ("BRRLUFBFFLRFDRUDLURDUFFRULFRDLRDUDBBLFULLUBUFDBDBBBLDR",
     "U' D' F D' B' L2 F' R D' F B R2 F2 R2 D' R2 F2 U2 D R2 F2 "),

    ("DRDUUBRRLBLLRRLUFDUFULFBFDLULFDDUDBBFRBDLUFFRBDRFBBRUL",
     "L' B R D' L B R D' F2 U2 F L2 F2 U B2 D F2 R2 D' B2 D2 "),

    ("LLFLUBRURDLUFRDRURUBFRFULBDDRBRDRLDUBUBDLDDFBLFUBBFFLF",
     "L B' R' U' F L U D2 B' R B2 R2 F2 D2 B2 U2 D B2 L2 U2 "),

    ("LLBRUFUBBUURURDLLRBDLRFBBLFLUUDDFRRFFDRRLFUFDDBDLBBDUF",
     "F L' U D B' L' U' D R' U2 F' D2 R2 U2 L2 F2 U L2 B2 L2 U "),

    ("FLLUUULLULBDRRFUFDUDBBFBBFRLRBBDURDBURFDLLFDDFURLBRRFD",
     "F2 B2 U2 B' U F2 D2 F B2 R F R2 U R2 D R2 L2 B2 U F2 D2 "),

    ("FURFUDBUDFLBFRBDRDUBRBFRULBFFRBDULDFUULRLRBDLULRLBDLFD",
     "U R L D R B U D F2 B2 R' U L2 B2 R2 U F2 D R2 B2 U' "),

    ("BFFBUFUBFDRDDRDFRDBRLFFBBDUDLLBDUUFLUURLLLFLRRDLRBUBUR",
     "F' B' U2 R' F' B2 R' F2 L U' R U' B2 L2 D L2 D B2 D' F2 D "),

    ("UFFDUULUUBFRLRFLDUDLRRFBBRDDUFDDFFBLLLBRLDDBRURBLBBFUR",
     "U D' F' R2 L' B2 R' L' D' L2 F' D' L2 U2 R2 F2 D' R2 F2 D' "),

    ("DDRBUUBUFUBFURLBRFDFRRFRFFULLRDDBLULBDRLLFUFUDRLDBBDLB",
     "U' R' B2 R F' R U2 D F2 U2 R' U' R2 U R2 D' B2 L2 F2 D2 "),

    ("BDRLUBDBDFRBFRRBFFRURRFUDDDLLLUDLFDUUUBBLFRRFUBLDBLLFU",
     "R2 F D L' D B U' L' D2 R' B' R2 D R2 F2 U' R2 D' F2 U' "),

    ("RFLUUFFDFDRBLRBRBRULLBFFUUFFFDLDDUDDURRBLRBULDDBLBUBRL",
     "F2 L B2 U2 B' L' D R' U R' F2 U F2 B2 R2 D' F2 B2 U' F2 "),

    ("DURFULUBUFDFLRFRUBLRLRFBFDBUBUFDRDFRBRBULDFLRDLLDBBDUL",
     "U L B2 R2 D' R B D2 F R L F R2 D R2 B2 D2 F2 U' D2 L2 B2 "),

    ("BRDFUBUBULULRRUDFUFRBDFUDFFRDLDDLFLFRULLLRDBBBFULBBRDR",
     "F2 R D L B2 U L2 B' R' U D' F' R2 F2 R2 D F2 U2 D B2 R2 U' "),

    ("LFDLUUDRDBBBRRUBFLFFLBFURDUFBRUDDUBFFDRRLLBLURLDFBDURL",
     "D' R B L' D R' D2 R F B L' U' R2 U' F2 L2 U' L2 D R2 U2 "),

    ("FUDLUBDLFLRBURFUDLLDUFFLBUFURRBDFRDBRFFDLRBLLRBDUBRDBU",
     "F' U D2 B2 L B' U' R2 F2 R' D' L2 U' B2 L2 D' R2 L2 B2 D "),

    ("LUFFUURDFDLURRDBBFUBLUFFBRDDDLLDRRLDBLBBLRUDRLFUFBURBF",
     "L F' L2 F D2 R2 L2 B2 U' F U D R2 D' B2 L2 F2 R2 U2 D' "),

    ("URDBUDLLBDFLBRUDLFBDRBFDDURLLFRDBULRBUUDLRLUFBFRFBRUFF",
     "B2 U2 L' B' R L2 F B R2 L F' U' B2 U B2 R2 U' R2 F2 B2 L2 "),

    ("RLFDUFFBLDUDBRLDFFLDBUFULLBBDRRDDFURURURLLLBURFBBBFURD",
     "U F' R2 F2 U' R F R2 D F2 R' F' D B2 U2 R2 B2 U2 R2 D F2 R2 "),

    ("BRDBUFBFBUURBRRFUUDLLDFDDDRLFULDLBULRURLLRDBFFFUBBDFRL",
     "F' D B2 R' L2 U2 B L' F' D L' U R2 U' L2 B2 D2 B2 D2 L2 B2 "),

    ("BRBFUURBFRRDURLBDDFRDFFBBLRUDDLDRUBFRUUFLDLULLFUBBLLDF",
     "U F' B R' D B' R U R' F U' L U' B2 U2 L2 U' R2 B2 L2 U F2 "),

    ("FLDRUBBRUBDRBRRLRFDFRDFUUUBFFDDDUULRDDRLLFBLLFULBBFUBL",
     "U R F' U' L' F R2 F R' U2 B L' F2 B2 U F2 L2 D L2 D R2 U2 "),

    ("BFRLURUFFLFBBRRDLDLLUDFRULFRDLFDURBRLBBRLBDUFUDDDBUFUB",
     "R B' D' L' U R D L' D R2 F D2 F2 D' R2 L2 B2 R2 U' R2 "),

    ("BDFBUUFDLUFDLRUFURDBFLFDUURLBUDDRDLBDRLFLFLRBRFRLBRUBB",
     "R L2 U F R2 D2 R' L2 U F' D' L' U' B2 U' L2 U F2 R2 D2 L2 D "),

    ("FDLBUBRLUBUFDRURRBDURFFLLDUDFFRDFDLLDLFRLUBBBUBLRBDUFR",
     "U R D' R U' B2 D2 R' B' D' F' L' U L2 D' F2 L2 D F2 U2 L2 U "),

    ("BBFRURDDLBFRDRFDLDFLUDFRFDFLBLUDBRULDURULFBLUURRLBFBBU",
     "U' F' D2 B' L' U2 R2 D R D2 R' F2 U L2 F2 D B2 D2 L2 D' R2 "),

    ("BDBBULRBRFBLLRDFFBURUDFUDUULFLUDRRFDDUBLLRFRFUBRLBFLDD",
     "U B' L' B L F B D' R L' F R U L2 F2 B2 D F2 D2 R2 U D2 "),

    ("URLBULDDULDBBRLRRFRRBFFLFLFDFDUDUURRBUBBLDLFLDFRUBDUBF",
     "U L2 U D2 R' D B2 L F D L2 B' R2 B2 D2 F2 U2 L2 F2 L2 U L2 "),

    ("LDUFULFRURDRLRULBDDFFRFBFBURDBBDUBFLULLDLURRDBFFLBRBUD",
     "F' U2 D' F U' F2 U' F D B' L' D2 F2 U R2 U' L2 B2 U' B2 U2 "),

    ("FDBBUDUBRDBLLRFBRRBUFRFULDDUFLFDURLUDRRLLDDUFULLRBFFBB",
     "R2 F' R L' U R' U2 F' D2 F R U' R2 U L2 U' B2 L2 U2 D B2 "),

    ("UFBBURLLBRFDBRRFURBDUDFLDBDLDRFDLUBDRUUFLRLDFLLFUBUBRF",
     "R D F' L F' L2 B' U' D' R D B' U2 F2 U' L2 B2 U' L2 D R2 L2 "),

    ("DURBULRULBUDRRRLDLDBULFFFBBULDDDRBBFLDFDLFUFRBFFUBLURR",
     "F U' R F' R L D2 L' B' D R F2 U' R2 B2 D R2 D2 R2 L2 B2 "),

    ("UFBLURRDLDURRRLUFFFBBFFDULRFFBRDUFBDLBUDLRLBLDDBUBLRUD",
     "B U R' D2 R2 D' B2 U' R B' U R2 D2 R2 B2 U F2 D' B2 U' "),

    ("FLBUUDFBDBFURRRUBLLULRFFLLFBDRBDLDRDRLUFLDBDURFDBBUFUR",
     "U' D' R' F' R2 U' D2 F U' L U R2 U2 L2 F2 R2 L2 U' F2 D' "),

    ("DRLUUBFBRBLURRLRUBLRDDFDLFUFUFFDBRDUBRUFLLFDDBFLUBLRBD",
     "D2 R' D' F2 B D R2 D2 R' F2 D' F2 U' B2 L2 U2 D R2 U "),
]

if __name__ == '__main__':

    cmd = './solve'

    if len(sys.argv) > 1:
        fname = sys.argv[1]
        logging.info('loading tests from %s', fname)
        with open(fname) as f:
            cnt = 0
            t = f.readline()
            while t:
                logging.info('running test %d...' % (cnt + 1))
                t = t.strip()
                r = f.readline().strip()
                res = subprocess.check_output(
                    [cmd, t], stderr=open(os.devnull, 'wb')).strip()
                logging.info(res)
                if res != r:
                    logging.error(
                        'Error for %s:\n\tmust be: %s\n\tgot: %s' % (t, repr(r), repr(res)))
                    sys.exit(1)
                cnt += 1
                t = f.readline()
            logging.info('all %d tests passed' % cnt)
    else:
        for i, tst in enumerate(javares):
            logging.info('running test %d of %d...' % (i + 1, len(javares)))
            t, r = tst
            res = subprocess.check_output(
                [cmd, t], stderr=open(os.devnull, 'wb')).strip()
            logging.info(res)
            if res != r.strip():
                logging.error(
                    'Error for %s:\n\tmust be: %s\n\tgot: %s' % (t, repr(r), repr(res)))
                sys.exit(1)
        logging.info('all %d tests passed' % len(javares))
