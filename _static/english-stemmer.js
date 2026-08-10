// Generated from english.sbl by Snowball 3.0.1 - https://snowballstem.org/

/**@constructor*/
var EnglishStemmer = function() {
    var base = new BaseStemmer();

    /** @const */ var a_0 = [
        ["arsen", -1, -1],
        ["commun", -1, -1],
        ["emerg", -1, -1],
        ["gener", -1, -1],
        ["later", -1, -1],
        ["organ", -1, -1],
        ["past", -1, -1],
        ["univers", -1, -1]
    ];

    /** @const */ var a_1 = [
        ["'", -1, 1],
        ["'s'", 0, 1],
        ["'s", -1, 1]
    ];

    /** @const */ var a_2 = [
        ["ied", -1, 2],
        ["s", -1, 3],
        ["ies", 1, 2],
        ["sses", 1, 1],
        ["ss", 1, -1],
        ["us", 1, -1]
    ];

    /** @const */ var a_3 = [
        ["succ", -1, 1],
        ["proc", -1, 1],
        ["exc", -1, 1]
    ];

    /** @const */ var a_4 = [
        ["even", -1, 2],
        ["cann", -1, 2],
        ["inn", -1, 2],
        ["earr", -1, 2],
        ["herr", -1, 2],
        ["out", -1, 2],
        ["y", -1, 1]
    ];

    /** @const */ var a_5 = [
        ["", -1, -1],
        ["ed", 0, 2],
        ["eed", 1, 1],
        ["ing", 0, 3],
        ["edly", 0, 2],
        ["eedly", 4, 1],
        ["ingly", 0, 2]
    ];

    /** @const */ var a_6 = [
        ["", -1, 3],
        ["bb", 0, 2],
        ["dd", 0, 2],
        ["ff", 0, 2],
        ["gg", 0, 2],
        ["bl", 0, 1],
        ["mm", 0, 2],
        ["nn", 0, 2],
        ["pp", 0, 2],
        ["rr", 0, 2],
        ["at", 0, 1],
        ["tt", 0, 2],
        ["iz", 0, 1]
    ];

    /** @const */ var a_7 = [
        ["anci", -1, 3],
        ["enci", -1, 2],
        ["ogi", -1, 14],
        ["li", -1, 16],
        ["bli", 3, 12],
        ["abli", 4, 4],
        ["alli", 3, 8],
        ["fulli", 3, 9],
        ["lessli", 3, 15],
        ["ousli", 3, 10],
        ["entli", 3, 5],
        ["aliti", -1, 8],
        ["biliti", -1, 12],
        ["iviti", -1, 11],
        ["tional", -1, 1],
        ["ational", 14, 7],
        ["alism", -1, 8],
        ["ation", -1, 7],
        ["ization", 17, 6],
        ["izer", -1, 6],
        ["ator", -1, 7],
        ["iveness", -1, 11],
        ["fulness", -1, 9],
        ["ousness", -1, 10],
        ["ogist", -1, 13]
    ];

    /** @const */ var a_8 = [
        ["icate", -1, 4],
        ["ative", -1, 6],
        ["alize", -1, 3],
        ["iciti", -1, 4],
        ["ical", -1, 4],
        ["tional", -1, 1],
        ["ational", 5, 2],
        ["ful", -1, 5],
        ["ness", -1, 5]
    ];

    /** @const */ var a_9 = [
        ["ic", -1, 1],
        ["ance", -1, 1],
        ["ence", -1, 1],
        ["able", -1, 1],
        ["ible", -1, 1],
        ["ate", -1, 1],
        ["ive", -1, 1],
        ["ize", -1, 1],
        ["iti", -1, 1],
        ["al", -1, 1],
        ["ism", -1, 1],
        ["ion", -1, 2],
        ["er", -1, 1],
        ["ous", -1, 1],
        ["ant", -1, 1],
        ["ent", -1, 1],
        ["ment", 15, 1],
        ["ement", 16, 1]
    ];

    /** @const */ var a_10 = [
        ["e", -1, 1],
        ["l", -1, 2]
    ];

    /** @const */ var a_11 = [
        ["andes", -1, -1],
        ["atlas", -1, -1],
        ["bias", -1, -1],
        ["cosmos", -1, -1],
        ["early", -1, 5],
        ["gently", -1, 3],
        ["howe", -1, -1],
        ["idly", -1, 2],
        ["news", -1, -1],
        ["only", -1, 6],
        ["singly", -1, 7],
        ["skies", -1, 1],
        ["sky", -1, -1],
        ["ugly", -1, 4]
    ];

    /** @const */ var /** Array<int> */ g_aeo = [17, 64];

    /** @const */ var /** Array<int> */ g_v = [17, 65, 16, 1];

    /** @const */ var /** Array<int> */ g_v_WXY = [1, 17, 65, 208, 1];

    /** @const */ var /** Array<int> */ g_valid_LI = [55, 141, 2];

    var /** boolean */ B_Y_found = false;
    var /** number */ I_p2 = 0;
    var /** number */ I_p1 = 0;


    /** @return {boolean} */
    function r_prelude() {
        B_Y_found = false;
        /** @const */ var /** number */ v_1 = base.cursor;
        lab0: {
            base.bra = base.cursor;
            if (!(base.eq_s("'")))
            {
                break lab0;
            }
            base.ket = base.cursor;
            if (!base.slice_del())
            {
                return false;
            }
        }
        base.cursor = v_1;
        /** @const */ var /** number */ v_2 = base.cursor;
        lab1: {
            base.bra = base.cursor;
            if (!(base.eq_s("y")))
            {
                break lab1;
            }
            base.ket = base.cursor;
            if (!base.slice_from("Y"))
            {
                return false;
            }
            B_Y_found = true;
        }
        base.cursor = v_2;
        /** @const */ var /** number */ v_3 = base.cursor;
        lab2: {
            while(true)
            {
                /** @const */ var /** number */ v_4 = base.cursor;
                lab3: {
                    golab4: while(true)
                    {
                        /** @const */ var /** number */ v_5 = base.cursor;
                        lab5: {
                            if (!(base.in_grouping(g_v, 97, 121)))
                            {
                                break lab5;
                            }
                            base.bra = base.cursor;
                            if (!(base.eq_s("y")))
                            {
                                break lab5;
                            }
                            base.ket = base.cursor;
                            base.cursor = v_5;
                            break golab4;
                        }
                        base.cursor = v_5;
                        if (base.cursor >= base.limit)
                        {
                            break lab3;
                        }
                        base.cursor++;
                    }
                    if (!base.slice_from("Y"))
                    {
                        return false;
                    }
                    B_Y_found = true;
                    continue;
                }
                base.cursor = v_4;
                break;
            }
        }
        base.cursor = v_3;
        return true;
    };

    /** @return {boolean} */
    function r_mark_regions() {
        I_p1 = base.limit;
        I_p2 = base.limit;
        /** @const */ var /** number */ v_1 = base.cursor;
        lab0: {
            lab1: {
                /** @const */ var /** number */ v_2 = base.cursor;
                lab2: {
                    if (base.find_among(a_0) == 0)
                    {
                        break lab2;
                    }
                    break lab1;
                }
                base.cursor = v_2;
                if (!base.go_out_grouping(g_v, 97, 121))
                {
                    break lab0;
                }
                base.cursor++;
                if (!base.go_in_grouping(g_v, 97, 121))
                {
                    break lab0;
                }
                base.cursor++;
            }
            I_p1 = base.cursor;
            if (!base.go_out_grouping(g_v, 97, 121))
            {
                break lab0;
            }
            base.cursor++;
            if (!base.go_in_grouping(g_v, 97, 121))
            {
                break lab0;
            }
            base.cursor++;
            I_p2 = base.cursor;
        }
        base.cursor = v_1;
        return true;
    };

    /** @return {boolean} */
    function r_shortv() {
        lab0: {
            /** @const */ var /** number */ v_1 = base.limit - base.cursor;
            lab1: {
                if (!(base.out_grouping_b(g_v_WXY, 89, 121)))
                {
                    break lab1;
                }
                if (!(base.in_grouping_b(g_v, 97, 121)))
                {
                    break lab1;
                }
                if (!(base.out_grouping_b(g_v, 97, 121)))
                {
                    break lab1;
                }
                break lab0;
            }
            base.cursor = base.limit - v_1;
            lab2: {
                if (!(base.out_grouping_b(g_v, 97, 121)))
                {
                    break lab2;
                }
                if (!(base.in_grouping_b(g_v, 97, 121)))
                {
                    break lab2;
                }
                if (base.cursor > base.limit_backward)
                {
                    break lab2;
                }
                break lab0;
            }
            base.cursor = base.limit - v_1;
            if (!(base.eq_s_b("past")))
            {
                return false;
            }
        }
        return true;
    };

    /** @return {boolean} */
    function r_R1() {
        return I_p1 <= base.cursor;
    };

    /** @return {boolean} */
    function r_R2() {
        return I_p2 <= base.cursor;
    };

    /** @return {boolean} */
    function r_Step_1a() {
        var /** number */ among_var;
        /** @const */ var /** number */ v_1 = base.limit - base.cursor;
        lab0: {
            base.ket = base.cursor;
            if (base.find_among_b(a_1) == 0)
            {
                base.cursor = base.limit - v_1;
                break lab0;
            }
            base.bra = base.cursor;
            if (!base.slice_del())
            {
                return false;
            }
        }
        base.ket = base.cursor;
        among_var = base.find_among_b(a_2);
        if (among_var == 0)
        {
            return false;
        }
        base.bra = base.cursor;
        switch (among_var) {
            case 1:
                if (!base.slice_from("ss"))
                {
                    return false;
                }
                break;
            case 2:
                lab1: {
                    /** @const */ var /** number */ v_2 = base.limit - base.cursor;
                    lab2: {
                        {
                            /** @const */ var /** number */ c1 = base.cursor - 2;
                            if (c1 < base.limit_backward)
                            {
                                break lab2;
                            }
                            base.cursor = c1;
                        }
                        if (!base.slice_from("i"))
                        {
                            return false;
                        }
                        break lab1;
                    }
                    base.cursor = base.limit - v_2;
                    if (!base.slice_from("ie"))
                    {
                        return false;
                    }
                }
                break;
            case 3:
                if (base.cursor <= base.limit_backward)
                {
                    return false;
                }
                base.cursor--;
                if (!base.go_out_grouping_b(g_v, 97, 121))
                {
                    return false;
                }
                base.cursor--;
                if (!base.slice_del())
                {
                    return false;
                }
                break;
        }
        return true;
    };

    /** @return {boolean} */
    function r_Step_1b() {
        var /** number */ among_var;
        base.ket = base.cursor;
        among_var = base.find_among_b(a_5);
        base.bra = base.cursor;
        lab0: {
            /** @const */ var /** number */ v_1 = base.limit - base.cursor;
            lab1: {
                switch (among_var) {
                    case 1:
                        /** @const */ var /** number */ v_2 = base.limit - base.cursor;
                        lab2: {
                            lab3: {
                                /** @const */ var /** number */ v_3 = base.limit - base.cursor;
                                lab4: {
                                    if (base.find_among_b(a_3) == 0)
                                    {
                                        break lab4;
                                    }
                                    if (base.cursor > base.limit_backward)
                                    {
                                        break lab4;
                                    }
                                    break lab3;
                                }
                                base.cursor = base.limit - v_3;
                                if (!r_R1())
                                {
                                    break lab2;
                                }
                                if (!base.slice_from("ee"))
                                {
                                    return false;
                                }
                            }
                        }
                        base.cursor = base.limit - v_2;
                        break;
                    case 2:
                        break lab1;
                    case 3:
                        among_var = base.find_among_b(a_4);
                        if (among_var == 0)
                        {
                            break lab1;
                        }
                        switch (among_var) {
                            case 1:
                                /** @const */ var /** number */ v_4 = base.limit - base.cursor;
                                if (!(base.out_grouping_b(g_v, 97, 121)))
                                {
                                    break lab1;
                                }
                                if (base.cursor > base.limit_backward)
                                {
                                    break lab1;
                                }
                                base.cursor = base.limit - v_4;
                                base.bra = base.cursor;
                                if (!base.slice_from("ie"))
                                {
                                    return false;
                                }
                                break;
                            case 2:
                                if (base.cursor > base.limit_backward)
                                {
                                    break lab1;
                                }
                                break;
                        }
                        break;
                }
                break lab0;
            }
            base.cursor = base.limit - v_1;
            /** @const */ var /** number */ v_5 = base.limit - base.cursor;
            if (!base.go_out_grouping_b(g_v, 97, 121))
            {
                return false;
            }
            base.cursor--;
            base.cursor = base.limit - v_5;
            if (!base.slice_del())
            {
                return false;
            }
            base.ket = base.cursor;
            base.bra = base.cursor;
            /** @const */ var /** number */ v_6 = base.limit - base.cursor;
            among_var = base.find_among_b(a_6);
            switch (among_var) {
                case 1:
                    if (!base.slice_from("e"))
                    {
                        return false;
                    }
                    return false;
                case 2:
                    {
                        /** @const */ var /** number */ v_7 = base.limit - base.cursor;
                        lab5: {
                            if (!(base.in_grouping_b(g_aeo, 97, 111)))
                            {
                                break lab5;
                            }
                            if (base.cursor > base.limit_backward)
                            {
                                break lab5;
                            }
                            return false;
                        }
                        base.cursor = base.limit - v_7;
                    }
                    break;
                case 3:
                    if (base.cursor != I_p1)
                    {
                        return false;
                    }
                    /** @const */ var /** number */ v_8 = base.limit - base.cursor;
                    if (!r_shortv())
                    {
                        return false;
                    }
                    base.cursor = base.limit - v_8;
                    if (!base.slice_from("e"))
                    {
                        return false;
                    }
                    return false;
            }
            base.cursor = base.limit - v_6;
            base.ket = base.cursor;
            if (base.cursor <= base.limit_backward)
            {
                return false;
            }
            base.cursor--;
            base.bra = base.cursor;
            if (!base.slice_del())
            {
                return false;
            }
        }
        return true;
    };

    /** @return {boolean} */
    function r_Step_1c() {
        base.ket = base.cursor;
        lab0: {
            /** @const */ var /** number */ v_1 = base.limit - base.cursor;
            lab1: {
                if (!(base.eq_s_b("y")))
                {
                    break lab1;
                }
                break lab0;
            }
            base.cursor = base.limit - v_1;
            if (!(base.eq_s_b("Y")))
            {
                return false;
            }
        }
        base.bra = base.cursor;
        if (!(base.out_grouping_b(g_v, 97, 121)))
        {
            return false;
        }
        lab2: {
            if (base.cursor > base.limit_backward)
            {
                break lab2;
            }
            return false;
        }
        if (!base.slice_from("i"))
        {
            return false;
        }
        return true;
    };

    /** @return {boolean} */
    function r_Step_2() {
        var /** number */ among_var;
        base.ket = base.cursor;
        among_var = base.find_among_b(a_7);
        if (among_var == 0)
        {
            return false;
        }
        base.bra = base.cursor;
        if (!r_R1())
        {
            return false;
        }
        switch (among_var) {
            case 1:
                if (!base.slice_from("tion"))
                {
                    return false;
                }
                break;
            case 2:
                if (!base.slice_from("ence"))
                {
                    return false;
                }
                break;
            case 3:
                if (!base.slice_from("ance"))
                {
                    return false;
                }
                break;
            case 4:
                if (!base.slice_from("able"))
                {
                    return false;
                }
                break;
            case 5:
                if (!base.slice_from("ent"))
                {
                    return false;
                }
                break;
            case 6:
                if (!base.slice_from("ize"))
                {
                    return false;
                }
                break;
            case 7:
                if (!base.slice_from("ate"))
                {
                    return false;
                }
                break;
            case 8:
                if (!base.slice_from("al"))
                {
                    return false;
                }
                break;
            case 9:
                if (!base.slice_from("ful"))
                {
                    return false;
                }
                break;
            case 10:
                if (!base.slice_from("ous"))
                {
                    return false;
                }
                break;
            case 11:
                if (!base.slice_from("ive"))
                {
                    return false;
                }
                break;
            case 12:
                if (!base.slice_from("ble"))
                {
                    return false;
                }
                break;
            case 13:
                if (!base.slice_from("og"))
                {
                    return false;
                }
                break;
            case 14:
                if (!(base.eq_s_b("l")))
                {
                    return false;
                }
                if (!base.slice_from("og"))
                {
                    return false;
                }
                break;
            case 15:
                if (!base.slice_from("less"))
                {
                    return false;
                }
                break;
            case 16:
                if (!(base.in_grouping_b(g_valid_LI, 99, 116)))
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
        }
        return true;
    };

    /** @return {boolean} */
    function r_Step_3() {
        var /** number */ among_var;
        base.ket = base.cursor;
        among_var = base.find_among_b(a_8);
        if (among_var == 0)
        {
            return false;
        }
        base.bra = base.cursor;
        if (!r_R1())
        {
            return false;
        }
        switch (among_var) {
            case 1:
                if (!base.slice_from("tion"))
                {
                    return false;
                }
                break;
            case 2:
                if (!base.slice_from("ate"))
                {
                    return false;
                }
                break;
            case 3:
                if (!base.slice_from("al"))
                {
                    return false;
                }
                break;
            case 4:
                if (!base.slice_from("ic"))
                {
                    return false;
                }
                break;
            case 5:
                if (!base.slice_del())
                {
                    return false;
                }
                break;
            case 6:
                if (!r_R2())
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
        }
        return true;
    };

    /** @return {boolean} */
    function r_Step_4() {
        var /** number */ among_var;
        base.ket = base.cursor;
        among_var = base.find_among_b(a_9);
        if (among_var == 0)
        {
            return false;
        }
        base.bra = base.cursor;
        if (!r_R2())
        {
            return false;
        }
        switch (among_var) {
            case 1:
                if (!base.slice_del())
                {
                    return false;
                }
                break;
            case 2:
                lab0: {
                    /** @const */ var /** number */ v_1 = base.limit - base.cursor;
                    lab1: {
                        if (!(base.eq_s_b("s")))
                        {
                            break lab1;
                        }
                        break lab0;
                    }
                    base.cursor = base.limit - v_1;
                    if (!(base.eq_s_b("t")))
                    {
                        return false;
                    }
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
        }
        return true;
    };

    /** @return {boolean} */
    function r_Step_5() {
        var /** number */ among_var;
        base.ket = base.cursor;
        among_var = base.find_among_b(a_10);
        if (among_var == 0)
        {
            return false;
        }
        base.bra = base.cursor;
        switch (among_var) {
            case 1:
                lab0: {
                    lab1: {
                        if (!r_R2())
                        {
                            break lab1;
                        }
                        break lab0;
                    }
                    if (!r_R1())
                    {
                        return false;
                    }
                    {
                        /** @const */ var /** number */ v_1 = base.limit - base.cursor;
                        lab2: {
                            if (!r_shortv())
                            {
                                break lab2;
                            }
                            return false;
                        }
                        base.cursor = base.limit - v_1;
                    }
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
            case 2:
                if (!r_R2())
                {
                    return false;
                }
                if (!(base.eq_s_b("l")))
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
        }
        return true;
    };

    /** @return {boolean} */
    function r_exception1() {
        var /** number */ among_var;
        base.bra = base.cursor;
        among_var = base.find_among(a_11);
        if (among_var == 0)
        {
            return false;
        }
        base.ket = base.cursor;
        if (base.cursor < base.limit)
        {
            return false;
        }
        switch (among_var) {
            case 1:
                if (!base.slice_from("sky"))
                {
                    return false;
                }
                break;
            case 2:
                if (!base.slice_from("idl"))
                {
                    return false;
                }
                break;
            case 3:
                if (!base.slice_from("gentl"))
                {
                    return false;
                }
                break;
            case 4:
                if (!base.slice_from("ugli"))
                {
                    return false;
                }
                break;
            case 5:
                if (!base.slice_from("earli"))
                {
                    return false;
                }
                break;
            case 6:
                if (!base.slice_from("onli"))
                {
                    return false;
                }
                break;
            case 7:
                if (!base.slice_from("singl"))
                {
                    return false;
                }
                break;
        }
        return true;
    };

    /** @return {boolean} */
    function r_postlude() {
        if (!B_Y_found)
        {
            return false;
        }
        while(true)
        {
            /** @const */ var /** number */ v_1 = base.cursor;
            lab0: {
                golab1: while(true)
                {
                    /** @const */ var /** number */ v_2 = base.cursor;
                    lab2: {
                        base.bra = base.cursor;
                        if (!(base.eq_s("Y")))
                        {
                            break lab2;
                        }
                        base.ket = base.cursor;
                        base.cursor = v_2;
                        break golab1;
                    }
                    base.cursor = v_2;
                    if (base.cursor >= base.limit)
                    {
                        break lab0;
                    }
                    base.cursor++;
                }
                if (!base.slice_from("y"))
                {
                    return false;
                }
                continue;
            }
            base.cursor = v_1;
            break;
        }
        return true;
    };

    this.stem = /** @return {boolean} */ function() {
        lab0: {
            /** @const */ var /** number */ v_1 = base.cursor;
            lab1: {
                if (!r_exception1())
                {
                    break lab1;
                }
                break lab0;
            }
            base.cursor = v_1;
            lab2: {
                {
                    /** @const */ var /** number */ v_2 = base.cursor;
                    lab3: {
                        {
                            /** @const */ var /** number */ c1 = base.cursor + 3;
                            if (c1 > base.limit)
                            {
                                break lab3;
                            }
                            base.cursor = c1;
                        }
                        break lab2;
                    }
                    base.cursor = v_2;
                }
                break lab0;
            }
            base.cursor = v_1;
            r_prelude();
            r_mark_regions();
            base.limit_backward = base.cursor; base.cursor = base.limit;
            /** @const */ var /** number */ v_3 = base.limit - base.cursor;
            r_Step_1a();
            base.cursor = base.limit - v_3;
            /** @const */ var /** number */ v_4 = base.limit - base.cursor;
            r_Step_1b();
            base.cursor = base.limit - v_4;
            /** @const */ var /** number */ v_5 = base.limit - base.cursor;
            r_Step_1c();
            base.cursor = base.limit - v_5;
            /** @const */ var /** number */ v_6 = base.limit - base.cursor;
            r_Step_2();
            base.cursor = base.limit - v_6;
            /** @const */ var /** number */ v_7 = base.limit - base.cursor;
            r_Step_3();
            base.cursor = base.limit - v_7;
            /** @const */ var /** number */ v_8 = base.limit - base.cursor;
            r_Step_4();
            base.cursor = base.limit - v_8;
            /** @const */ var /** number */ v_9 = base.limit - base.cursor;
            r_Step_5();
            base.cursor = base.limit - v_9;
            base.cursor = base.limit_backward;
            /** @const */ var /** number */ v_10 = base.cursor;
            r_postlude();
            base.cursor = v_10;
        }
        return true;
    };

    /**@return{string}*/
    this['stemWord'] = function(/**string*/word) {
        base.setCurrent(word);
        this.stem();
        return base.getCurrent();
    };
};
