
;
; UNIFICATION.
(O (name simple_unify) (^ (guy-nn e1 x1) (guy-nn e2 x2) )
   (label (^ (= x1 x2) ) ) )

(O (name schema) (^ (sell-vb e1 x1 x2 x3) (gm-nn e2 x1) (buy-vb e3 y1 y2 y3) (naoya-nn e4 y1) )
   (label (^ (= y1 x1) ) )
   )

; 
; ARGUMENT CONSTRAINTS.

; Mario says that Peach is cute. Mario says that he hates Luigi. (e2 and e4 should NOT be unified)
(O (name ac_1) (^ (mario-nn e1 x1) (say-vb e2 x1 e2 u1) (peach-nn e3 x2) (cute-adj e4 x2) (say-vb e5 x1 e4 u2) (luigi-nn e6 x3) (hate-vb e7 x1 x3 u3) ) )

; Mario says that Peach is cute. Mario says that Peach is cute. (e2 and e4 should be unified)
(O (name ac_2) (^ (mario-nn x1) (say-vb e1 x1 e2 u1) (peach-nn x2) (cute-adj e2 x2) (say-vb e3 x1 e4 u2) (cute-adj e4 x2) ) )

; Mario says that Peach is cute. Mario says that Peach is sweet. (e2 and e4 should be unified)
(B (=> (cute-adj e x) (sweet-adj e x) ) )
(O (name ac_3) (^ (mario-nn x1) (say-vb e1 x1 e2 u1) (peach-nn x2) (cute-adj e2 x2) (say-vb e3 x1 e4 u2) (sweet-adj e4 x2) ) )

;
; EXPLICIT NON-IDENTITY. (x1 and x2 in the examples below should not be unified)

; A guy is unlike another guy.
(O (name enid_single) (^ (guy-nn x1) (guy-nn x2) (unlike-in e1 x1 x2) )
   (label (^ (!= x1 x2) ) ) )

; A guy is separate from another guy (?).
(O (name enid_multi)  (^ (guy-nn x1) (guy-nn x2) (separate-adj e1 x1) (from-in e2 e1 x2) )
   (label (^ (!= x1 x2) ) ) )


;
; NAMED ENTITIES.

; Mario jumped. Luigi also jumped. (x1 and x2 should NOT be unified)
(O (name nedisj_1) (^ (mario-nn e1 x1) (luigi-nn e2 x2) (jump-vb e3 x1 u1 u2) (jump-vb e4 x2 u3 u4) (@per e5 x1) (@per e6 x2) )
   (label (^ (!= x1 x2) ) ) )

; Lennon jumped. John Lennon jumped. (x1 and x2 should be unified)
(O (name nedisj_2) (^ (lennon-nn e1 x1) (john-lennon-nn e2 x2) (jump-vb e3 x1 u1 u2) (jump-vb e4 x2 u3 u4) (@per e5 x1) (@per e6 x2) )
   (label (^ (= x1 x2) ) ) )


;
; DISJOINTNESS.
(O (name wndisj_1) (^ (cat-nn e1 x1) (dog-nn e2 x2) (cute-adj e3 x1) (cute-adj e4 x2) ) (label (^ (!= x1 x2) ) ) )
(O (name wndisj_2) (^ (puppy-nn e1 x1) (dog-nn e2 x2) (cute-adj e3 x1) (cute-adj e4 x2) ) (label (^ (= x1 x2) ) ) )
(O (name wnanto_1) (^ (male e1 x1) (rise-vb e2 x1 u1 u2) (male e3 x2) (fall-vb e4 x2 u3 u4) ) )

;
; FUNCTIONAL RELATIONS.

; Place 1 is the capital of German. Place 2 is the capital of German. (x1 and x2 should NOT be unified)
(O (name funcrel_unify_1)
   (^ (place-nn e1 x1) (equal eq1 x1 x3) (place-nn e2 x2) (equal eq2 x2 x5)
      (capital-nn e3 x3) (of-in e4 x3 x4) (german-nn e5 x4) (country-nn e6 x4)
      (capital-nn e7 x5) (of-in e8 x5 x6) (japan-nn e9 x6) (country-nn e10 x6) )
   (label (^ (!= x1 x2) ) )
   )

; Place 1 is the capital of German. Place 2 is the capital of German. (x1 and x2 should be unified)
(O (name funcrel_unify_2)
   (^ (place-nn e1 x1) (equal eq1 x1 x3) (place-nn e2 x2) (equal eq2 x2 x5)
      (capital-nn e3 x3) (of-in e4 x3 x4) (german-nn e5 x4) (country-nn e6 x4)
      (capital-nn e7 x5) (of-in e8 x5 x4) )
   (label (^ (= x1 x2) ) )
   )

