"""Scripted trajectories for my seven added positive Problem A cases."""

SCRIPTED_CASES = {'CLM-9061': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9061"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue '
              'the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9061","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180,"refused_total":0,"evidence":[]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180,"refused_total":0,"evidence":[]}}'],
 'CLM-9062': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9062"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-3390"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"80053","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue '
              'the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9062","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"80053","disposition":"approved","amount":90}],"approved_total":90,"refused_total":0,"evidence":[]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"80053","disposition":"approved","amount":90}],"approved_total":90,"refused_total":0,"evidence":[]}}'],
 'CLM-9063': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9063"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-6118"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-330"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-6118","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue '
              'the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9063","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":200}],"approved_total":200,"refused_total":0,"evidence":[]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":200}],"approved_total":200,"refused_total":0,"evidence":[]}}'],
 'CLM-9064': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9064"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"27447","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-5502","procedure_code":"27447","date_of_service":"2026-10-26"}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue '
              'the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9064","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"27447","disposition":"approved","amount":5000,"preauthorisation_id":"PA-5702"}],"approved_total":5000,"refused_total":0,"evidence":["PA-5702 '
              'cited for line 27447","PA-5702 is valid on 2026-10-26"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"27447","disposition":"approved","amount":5000,"preauthorisation_id":"PA-5702"}],"approved_total":5000,"refused_total":0,"evidence":["PA-5702 '
              'cited for line 27447","PA-5702 is valid on 2026-10-26"]}}'],
 'CLM-9065': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9065"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"47120","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"70553","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue '
              'the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9065","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1400},{"procedure_code":"70553","disposition":"approved","amount":500}],"approved_total":1900,"refused_total":0,"evidence":[]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1400},{"procedure_code":"70553","disposition":"approved","amount":500}],"approved_total":1900,"refused_total":0,"evidence":[]}}'],
 'CLM-9066': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9066"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-6118"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-6118","procedure_code":"99213","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-6118","procedure_code":"70553","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue '
              'the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9066","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"70553","disposition":"approved","amount":620}],"approved_total":800,"refused_total":0,"evidence":[]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"70553","disposition":"approved","amount":620}],"approved_total":800,"refused_total":0,"evidence":[]}}'],
 'CLM-9067': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9067"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-3390"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-330"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue '
              'the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9067","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":250}],"approved_total":250,"refused_total":0,"evidence":[]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":250}],"approved_total":250,"refused_total":0,"evidence":[]}}']}
