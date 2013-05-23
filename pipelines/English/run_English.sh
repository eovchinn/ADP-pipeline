#! /bin/bash

# usage:
# $ ./run_English.sh <input> <output>
# or
# $ ./run_English.sh <input>
# or
# $ ./run_English.sh

TOKENIZER_BIN=$BOXER_DIR/bin/tokkie
CANDC_BIN=$BOXER_DIR/bin/candc
BOXER_BIN=$BOXER_DIR/bin/boxer

TOKENIZER_OPT="--stdin"
CANDC_OPT="--models $BOXER_DIR/models/boxer --candc-printer boxer"
BOXER_OPT="--semantics tacitus --resolve true --stdin"


if [ -d "$2" ]; then
	$TOKENIZER_BIN $TOKENIZER_OPT < "${1:-/dev/stdin}" |
	tee $2/tmp.tok |
	$CANDC_BIN $CANDC_OPT |
	tee $2/tmp.candc |
	$BOXER_BIN $BOXER_OPT > /dev/stdout
else
	$TOKENIZER_BIN $TOKENIZER_OPT < "${1:-/dev/stdin}" |
	$CANDC_BIN $CANDC_OPT |
	$BOXER_BIN $BOXER_OPT > "${2:-/dev/stdout}"
fi
