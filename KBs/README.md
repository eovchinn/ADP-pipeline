Knowledge Bases
===

Available abductive knowledge bases are stored in this directory.
Abductive axioms have the following format:

```
<axiom> ::= "(B (name " <axiom name> ") (=> " <lhs> <rhs> "))"
<axiom name> ::= <ASCII stringl, no spaces>
<lhs> ::= <proposition with weight> | "(^ " <conjunction of propositions with weights> ")"
<rhs> ::= <proposition> | "(^ " <conjunction of propositions> ")"
<conjunction of propositions with weights> ::= <proposition with weight> | <proposition with weight> " " <conjunction of propositions with weights>
<conjunction of propositions> ::= <proposition> | <proposition> " " <conjunction of propositions>
<proposition with weight> ::= "(" <proposition name> " " <arguments> " :" <weight> ")"
<proposition> ::= "(" <proposition name> " " <arguments> ")"
<proposition name> ::= <UTF-8 string, no spaces>
<arguments> ::= "" | <argument> | <argument> " " <arguments>
<argument> ::= <ASCII string, no spaces>
```

Example:

```
(B (name conflict-with) (=> (conflict e x y g h :0.9) (^ (conflict-vb e g u1 u2)(with-in e1 e y))))
```

A knowledge base can be compiled by [Henry](https://github.com/naoya-i/henry-n700) using the following command:

```
henry -m compile_kb KB_PATH -o KB_COMPILED_PATH
```


