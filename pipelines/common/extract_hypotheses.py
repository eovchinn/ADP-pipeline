import re
import json

def main():
	lines = sys.stdin

	output_struct = []
	hypothesis_found = False
	p = re.compile('<result-inference target="(.+)"')
	target = ''
	hypothesis = ''
	unification = False
	explanation = False

	for line in lines:
		output_struct_item={} 
		matchObj = p.match(line)
		if matchObj: target = matchObj.group(1)	
		elif line.startswith('<hypothesis'): hypothesis_found = True
		elif line.startswith('</hypothesis>'): hypothesis_found = False 
		elif hypothesis_found: hypothesis = line
		elif line.startswith('<unification'): unification = True
		elif line.startswith('<explanation'): explanation = True
		elif line.startswith('</result-inference>'):
			output_struct_item['annotation_id'] = target
			output_struct_item['abductive_hypothesis'] = hypothesis
			output_struct_item['abductive_unification'] = unification
			output_struct_item['abductive_explanation'] = explanation
			output_struct_item['description'] = 'Abductive engine output; abductive_hypothesis: metaphor interpretation; abductive_unification: unifications happened or not; abductive_explanation: axioms applied or not'
			output_struct.append(output_struct_item) 
			target = ''
			unification = False
			explanation = False

	return json.dumps(output_struct)

if "__main__" == __name__: main()