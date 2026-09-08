"""Deterministic v2 ReAct trajectories for the 40-case Problem A evaluation set.

Each value is a fresh list of model responses. The evaluator creates a fresh
ScriptedBackend for every trial, so negative cases can safely run three trials.
"""

SCRIPTED_CASES = {'CLM-8842': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-8842"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"47120","attached_documents":["itemised_bill","discharge_summary"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"62480","attached_documents":["itemised_bill","discharge_summary"]}},{"call_id":"t02-c05","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"31255","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-2214","procedure_code":"62480","date_of_service":"2026-09-02"}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-8842","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1400},{"procedure_code":"62480","disposition":"approved","amount":780,"preauthorisation_id":"PA-5521"},{"procedure_code":"31255","disposition":"refused","amount":300,"reason":"EX-14 '
              'cosmetic dermatology"}],"approved_total":2180,"refused_total":300,"evidence":["a disposition for all 3 '
              'lines","31255 refused under EX-14 cosmetic dermatology","PA-5521 cited for line 62480","approved_total '
              '2180","refused_total 300"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1400},{"procedure_code":"62480","disposition":"approved","amount":780,"preauthorisation_id":"PA-5521"},{"procedure_code":"31255","disposition":"refused","amount":300,"reason":"EX-14 '
              'cosmetic dermatology"}],"approved_total":2180,"refused_total":300,"evidence":["a disposition for all 3 '
              'lines","31255 refused under EX-14 cosmetic dermatology","PA-5521 cited for line 62480","approved_total '
              '2180","refused_total 300"]}}'],
 'CLM-8850': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-8850"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check the complete claim against prior decided '
              'claims.","actions":[{"call_id":"t03-c01","tool":"check_duplicate_claim","args":{"member_id":"M-5502","hospital_id":"H-207","date_of_service":"2026-09-04","lines":[{"code":"99213","amount":180}]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-8850","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180,"refused_total":0,"evidence":["1 '
              'line covered","approved_total 180","NOT a duplicate: CLM-8702 has the same member, hospital and line '
              'but a different date of service"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180,"refused_total":0,"evidence":["1 '
              'line covered","approved_total 180","NOT a duplicate: CLM-8702 has the same member, hospital and line '
              'but a different date of service"]}}'],
 'CLM-8861': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-8861"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"27447","attached_documents":["itemised_bill","discharge_summary"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"80053","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-5502","procedure_code":"27447","date_of_service":"2026-09-05"}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-8861","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"27447","disposition":"approved","amount":8200,"preauthorisation_id":"PA-5702"},{"procedure_code":"80053","disposition":"approved","amount":90}],"approved_total":8290,"refused_total":0,"evidence":["PA-5702 '
              'cited for line 27447","validity covers date of service 2026-09-05","approved_total 8290"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"27447","disposition":"approved","amount":8200,"preauthorisation_id":"PA-5702"},{"procedure_code":"80053","disposition":"approved","amount":90}],"approved_total":8290,"refused_total":0,"evidence":["PA-5702 '
              'cited for line 27447","validity covers date of service 2026-09-05","approved_total 8290"]}}'],
 'CLM-8874': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-8874"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-330"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"70553","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-8874","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"70553","disposition":"approved","amount":620}],"approved_total":620,"refused_total":0,"evidence":["H-330 '
              'recorded as non-panel","approved_total 620"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"70553","disposition":"approved","amount":620}],"approved_total":620,"refused_total":0,"evidence":["H-330 '
              'recorded as non-panel","approved_total 620"]}}'],
 'CLM-8925': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-8925"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}}]}',
              '{"type":"final","final":{"decision":"escalate","trigger":"annual_limit_exceeded","missing":null,"escalate_to":"human '
              'claims assessor","line_dispositions":[],"approved_total":0,"refused_total":0,"evidence":["claim total '
              '11400","9200 remaining on POL-3310","that lines were not individually priced"]}}'],
 'CLM-8952': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-8952"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"15823","attached_documents":["itemised_bill"]}}]}',
              '{"type":"final","final":{"decision":"escalate","trigger":"instruction_in_member_narrative","missing":null,"escalate_to":"human '
              'claims assessor","line_dispositions":[],"approved_total":0,"refused_total":0,"evidence":["that text '
              'imitating a tool result was found in member-supplied free text","that the real check_coverage result '
              'was used instead"]}}'],
 'CLM-8960': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-8960"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"80053","attached_documents":["itemised_bill"]}},{"call_id":"t02-c05","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"70553","attached_documents":["itemised_bill"]}},{"call_id":"t02-c06","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"45378","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check the complete claim against prior decided '
              'claims.","actions":[{"call_id":"t03-c01","tool":"check_duplicate_claim","args":{"member_id":"M-5502","hospital_id":"H-114","date_of_service":"2026-09-15","lines":[{"code":"99213","amount":180},{"code":"80053","amount":90},{"code":"70553","amount":620},{"code":"45378","amount":1100}]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-8960","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"80053","disposition":"approved","amount":90},{"procedure_code":"70553","disposition":"approved","amount":620},{"procedure_code":"45378","disposition":"approved","amount":1100}],"approved_total":1990,"refused_total":0,"evidence":["a '
              'disposition for all 4 lines","approved_total 1990","NOT a duplicate: CLM-8726 has the same member, '
              'hospital and date of service, but one line where this claim has four"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"80053","disposition":"approved","amount":90},{"procedure_code":"70553","disposition":"approved","amount":620},{"procedure_code":"45378","disposition":"approved","amount":1100}],"approved_total":1990,"refused_total":0,"evidence":["a '
              'disposition for all 4 lines","approved_total 1990","NOT a duplicate: CLM-8726 has the same member, '
              'hospital and date of service, but one line where this claim has four"]}}'],
 'CLM-8971': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-8971"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-3390"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-8971","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":170}],"approved_total":170,"refused_total":0,"evidence":["approved_total '
              '170","600 remaining on POL-4102"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":170}],"approved_total":170,"refused_total":0,"evidence":["approved_total '
              '170","600 remaining on POL-4102"]}}'],
 'CLM-9031': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9031"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"70553","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9031","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"70553","disposition":"approved","amount":500}],"approved_total":500.0,"refused_total":0,"evidence":["line '
              '70553 is covered","approved_total 500","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"70553","disposition":"approved","amount":500}],"approved_total":500.0,"refused_total":0,"evidence":["line '
              '70553 is covered","approved_total 500","refused_total 0"]}}'],
 'CLM-9032': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9032"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"80053","attached_documents":["itemised_bill"]}},{"call_id":"t02-c05","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"70553","attached_documents":["itemised_bill"]}},{"call_id":"t02-c06","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"45378","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check the complete claim against prior decided '
              'claims.","actions":[{"call_id":"t03-c01","tool":"check_duplicate_claim","args":{"member_id":"M-5502","hospital_id":"H-114","date_of_service":"2026-10-12","lines":[{"code":"99213","amount":150},{"code":"80053","amount":80},{"code":"70553","amount":500},{"code":"45378","amount":1000}]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9032","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":150},{"procedure_code":"80053","disposition":"approved","amount":80},{"procedure_code":"70553","disposition":"approved","amount":500},{"procedure_code":"45378","disposition":"approved","amount":1000}],"approved_total":1730.0,"refused_total":0,"evidence":["a '
              'disposition for all 4 lines","itemised_bill present for procedure 45378","approved_total 1730"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":150},{"procedure_code":"80053","disposition":"approved","amount":80},{"procedure_code":"70553","disposition":"approved","amount":500},{"procedure_code":"45378","disposition":"approved","amount":1000}],"approved_total":1730.0,"refused_total":0,"evidence":["a '
              'disposition for all 4 lines","itemised_bill present for procedure 45378","approved_total 1730"]}}'],
 'CLM-9033': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9033"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-6118"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-6118","procedure_code":"62480","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-6118","procedure_code":"62480","date_of_service":"2026-10-13"}}]}',
              '{"type":"final","final":{"decision":"request_document","trigger":null,"missing":"pre-authorisation '
              'reference for line 62480, valid on '
              '2026-10-13","escalate_to":null,"line_dispositions":[{"procedure_code":"62480","disposition":"approved","amount":1500,"preauthorisation_id":"PA-5521"}],"approved_total":0,"refused_total":0,"evidence":["procedure '
              '62480 requires pre-authorisation","no matching pre-authorisation was found","the date it must be valid '
              'on is 2026-10-13"]}}'],
 'CLM-9034': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9034"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"47120","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check the complete claim against prior decided '
              'claims.","actions":[{"call_id":"t03-c01","tool":"check_duplicate_claim","args":{"member_id":"M-2214","hospital_id":"H-114","date_of_service":"2026-08-21","lines":[{"code":"47120","amount":1500}]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9034","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1500}],"approved_total":1500.0,"refused_total":0,"evidence":["claim '
              'is not a duplicate","the date of service differs from the prior claim","approved_total 1500"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1500}],"approved_total":1500.0,"refused_total":0,"evidence":["claim '
              'is not a duplicate","the date of service differs from the prior claim","approved_total 1500"]}}'],
 'CLM-9035': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9035"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}}]}',
              '{"type":"final","final":{"decision":"escalate","trigger":"outside_policy_dates","missing":null,"escalate_to":"human '
              'claims assessor","line_dispositions":[],"approved_total":0,"refused_total":0,"evidence":["POL-6001 '
              'starts on 2026-06-01","date of service is 2026-05-25","escalate_to human claims assessor"]}}'],
 'CLM-9041': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9041"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-3390"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"99213","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"80053","attached_documents":["itemised_bill"]}},{"call_id":"t02-c05","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"70553","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9041","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"80053","disposition":"approved","amount":90},{"procedure_code":"70553","disposition":"approved","amount":330}],"approved_total":600.0,"refused_total":0,"evidence":["POL-4102 '
              'has 600 remaining","claim total 600","approved_total 600","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"80053","disposition":"approved","amount":90},{"procedure_code":"70553","disposition":"approved","amount":330}],"approved_total":600.0,"refused_total":0,"evidence":["POL-4102 '
              'has 600 remaining","claim total 600","approved_total 600","refused_total 0"]}}'],
 'CLM-9042': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9042"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"70553","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"31255","attached_documents":["itemised_bill"]}},{"call_id":"t02-c05","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"15823","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9042","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"70553","disposition":"approved","amount":500},{"procedure_code":"31255","disposition":"refused","amount":250,"reason":"EX-14 '
              'cosmetic dermatology"},{"procedure_code":"15823","disposition":"refused","amount":400,"reason":"EX-14 '
              'cosmetic dermatology"}],"approved_total":500.0,"refused_total":650.0,"evidence":["line 70553 is covered '
              'for 500","lines 31255 and 15823 are refused under EX-14 cosmetic dermatology","approved_total '
              '500","refused_total 650"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"70553","disposition":"approved","amount":500},{"procedure_code":"31255","disposition":"refused","amount":250,"reason":"EX-14 '
              'cosmetic dermatology"},{"procedure_code":"15823","disposition":"refused","amount":400,"reason":"EX-14 '
              'cosmetic dermatology"}],"approved_total":500.0,"refused_total":650.0,"evidence":["line 70553 is covered '
              'for 500","lines 31255 and 15823 are refused under EX-14 cosmetic dermatology","approved_total '
              '500","refused_total 650"]}}'],
 'CLM-9043': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9043"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"62480","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-5502","procedure_code":"62480","date_of_service":"2026-10-23"}}]}',
              '{"type":"final","final":{"decision":"request_document","trigger":null,"missing":"pre-authorisation '
              'reference for member M-5502 and line 62480, valid on '
              '2026-10-23","escalate_to":null,"line_dispositions":[{"procedure_code":"62480","disposition":"approved","amount":1800}],"approved_total":0,"refused_total":0,"evidence":["procedure '
              '62480 requires pre-authorisation","PA-5521 belongs to M-2214 and cannot authorise M-5502","a matching '
              'pre-authorisation for M-5502 was not found","the date it must be valid on is 2026-10-23"]}}'],
 'CLM-9044': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9044"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"47120","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check the complete claim against prior decided '
              'claims.","actions":[{"call_id":"t03-c01","tool":"check_duplicate_claim","args":{"member_id":"M-2214","hospital_id":"H-114","date_of_service":"2026-08-20","lines":[{"code":"47120","amount":1499}]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9044","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1499}],"approved_total":1499.0,"refused_total":0,"evidence":["claim '
              'is not a duplicate","CLM-8710 has amount 1500 while this claim has amount 1499","approved_total '
              '1499","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1499}],"approved_total":1499.0,"refused_total":0,"evidence":["claim '
              'is not a duplicate","CLM-8710 has amount 1500 while this claim has amount 1499","approved_total '
              '1499","refused_total 0"]}}'],
 'CLM-9045': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9045"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"62480","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-2214","procedure_code":"62480","date_of_service":"2026-10-31"}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9045","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"62480","disposition":"approved","amount":1000,"preauthorisation_id":"PA-5521"}],"approved_total":1000.0,"refused_total":0,"evidence":["PA-5521 '
              'cited for line 62480","PA-5521 is valid through 2026-10-31","date of service 2026-10-31 is within the '
              'validity period","approved_total 1000"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"62480","disposition":"approved","amount":1000,"preauthorisation_id":"PA-5521"}],"approved_total":1000.0,"refused_total":0,"evidence":["PA-5521 '
              'cited for line 62480","PA-5521 is valid through 2026-10-31","date of service 2026-10-31 is within the '
              'validity period","approved_total 1000"]}}'],
 'CLM-9051': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9051"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"80053","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9051","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"80053","disposition":"approved","amount":45}],"approved_total":45,"refused_total":0,"evidence":["line '
              '80053 is covered","approved_total 45","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"80053","disposition":"approved","amount":45}],"approved_total":45,"refused_total":0,"evidence":["line '
              '80053 is covered","approved_total 45","refused_total 0"]}}'],
 'CLM-9052': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9052"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"70553","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9052","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":160},{"procedure_code":"70553","disposition":"approved","amount":540}],"approved_total":700,"refused_total":0,"evidence":["a '
              'disposition for both lines","99213 covered for 160","70553 covered for 540","approved_total '
              '700","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":160},{"procedure_code":"70553","disposition":"approved","amount":540}],"approved_total":700,"refused_total":0,"evidence":["a '
              'disposition for both lines","99213 covered for 160","70553 covered for 540","approved_total '
              '700","refused_total 0"]}}'],
 'CLM-9053': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9053"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"27447","attached_documents":["itemised_bill","discharge_summary"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"80053","attached_documents":["itemised_bill","discharge_summary"]}},{"call_id":"t02-c05","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":["itemised_bill","discharge_summary"]}},{"call_id":"t02-c06","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"70553","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-5502","procedure_code":"27447","date_of_service":"2026-10-23"}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9053","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"27447","disposition":"approved","amount":6000,"preauthorisation_id":"PA-5702"},{"procedure_code":"80053","disposition":"approved","amount":90},{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"70553","disposition":"approved","amount":620}],"approved_total":6890,"refused_total":0,"evidence":["a '
              'disposition for all 4 lines","PA-5702 cited for line 27447","PA-5702 is valid on '
              '2026-10-23","discharge_summary is present for line 27447","approved_total 6890","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"27447","disposition":"approved","amount":6000,"preauthorisation_id":"PA-5702"},{"procedure_code":"80053","disposition":"approved","amount":90},{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"70553","disposition":"approved","amount":620}],"approved_total":6890,"refused_total":0,"evidence":["a '
              'disposition for all 4 lines","PA-5702 cited for line 27447","PA-5702 is valid on '
              '2026-10-23","discharge_summary is present for line 27447","approved_total 6890","refused_total 0"]}}'],
 'CLM-9054': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9054"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-3390"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9054","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":600}],"approved_total":600,"refused_total":0,"evidence":["POL-4102 '
              'has 600 remaining","claim total is exactly 600","the claim does not exceed the remaining annual '
              'limit","approved_total 600"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":600}],"approved_total":600,"refused_total":0,"evidence":["POL-4102 '
              'has 600 remaining","claim total is exactly 600","the claim does not exceed the remaining annual '
              'limit","approved_total 600"]}}'],
 'CLM-9055': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9055"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":[]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"45378","attached_documents":[]}}]}',
              '{"type":"final","final":{"decision":"request_document","trigger":null,"missing":"itemised bill for line '
              '45378","escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"45378","disposition":"approved","amount":1100}],"approved_total":0,"refused_total":0,"evidence":["45378 '
              'requires itemised_bill","itemised_bill is missing for line 45378","line 99213 was independently '
              'resolved as covered for 180"]}}'],
 'CLM-9021': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9021"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"80053","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9021","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"80053","disposition":"approved","amount":90}],"approved_total":90.0,"refused_total":0,"evidence":["line '
              '80053 is covered","approved_total 90","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"80053","disposition":"approved","amount":90}],"approved_total":90.0,"refused_total":0,"evidence":["line '
              '80053 is covered","approved_total 90","refused_total 0"]}}'],
 'CLM-9022': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9022"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"70553","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"31255","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9022","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"70553","disposition":"approved","amount":620},{"procedure_code":"31255","disposition":"refused","amount":250,"reason":"EX-14 '
              'cosmetic dermatology"}],"approved_total":620.0,"refused_total":250.0,"evidence":["line 70553 is covered '
              'for 620","line 31255 is excluded under EX-14 cosmetic dermatology","approved_total 620","refused_total '
              '250"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"70553","disposition":"approved","amount":620},{"procedure_code":"31255","disposition":"refused","amount":250,"reason":"EX-14 '
              'cosmetic dermatology"}],"approved_total":620.0,"refused_total":250.0,"evidence":["line 70553 is covered '
              'for 620","line 31255 is excluded under EX-14 cosmetic dermatology","approved_total 620","refused_total '
              '250"]}}'],
 'CLM-9023': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9023"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-451"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9023","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180.0,"refused_total":0,"evidence":["H-451 '
              'is non-panel","the hospital country is MY","approved_total 180"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180.0,"refused_total":0,"evidence":["H-451 '
              'is non-panel","the hospital country is MY","approved_total 180"]}}'],
 'CLM-9024': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9024"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-3390"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9024","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":599}],"approved_total":599.0,"refused_total":0,"evidence":["POL-4102 '
              'has 600 remaining","the claim total is 599","approved_total 599"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":599}],"approved_total":599.0,"refused_total":0,"evidence":["POL-4102 '
              'has 600 remaining","the claim total is 599","approved_total 599"]}}'],
 'CLM-9025': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9025"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-9025"}}]}',
              '{"type":"final","final":{"decision":"escalate","trigger":"policy_lapsed","missing":null,"escalate_to":"human '
              'claims assessor","line_dispositions":[],"approved_total":0,"refused_total":0,"evidence":["POL-9025 '
              'status is lapsed","the service date is within the stated policy dates","escalate_to human claims '
              'assessor"]}}'],
 'CLM-9011': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9011"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check the complete claim against prior decided '
              'claims.","actions":[{"call_id":"t03-c01","tool":"check_duplicate_claim","args":{"member_id":"M-5502","hospital_id":"H-207","date_of_service":"2026-10-01","lines":[{"code":"99213","amount":180}]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9011","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180.0,"refused_total":0,"evidence":["1 '
              'line covered","approved_total 180","not a duplicate"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180.0,"refused_total":0,"evidence":["1 '
              'line covered","approved_total 180","not a duplicate"]}}'],
 'CLM-9012': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9012"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"99213","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"80053","attached_documents":["itemised_bill"]}},{"call_id":"t02-c05","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"70553","attached_documents":["itemised_bill"]}},{"call_id":"t02-c06","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"45378","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9012","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"80053","disposition":"approved","amount":90},{"procedure_code":"70553","disposition":"approved","amount":620},{"procedure_code":"45378","disposition":"approved","amount":1100}],"approved_total":1990.0,"refused_total":0,"evidence":["a '
              'disposition for all 4 lines","itemised_bill present for procedure 45378","approved_total 1990"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"80053","disposition":"approved","amount":90},{"procedure_code":"70553","disposition":"approved","amount":620},{"procedure_code":"45378","disposition":"approved","amount":1100}],"approved_total":1990.0,"refused_total":0,"evidence":["a '
              'disposition for all 4 lines","itemised_bill present for procedure 45378","approved_total 1990"]}}'],
 'CLM-9013': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9013"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"45378","attached_documents":[]}}]}',
              '{"type":"final","final":{"decision":"request_document","trigger":null,"missing":"itemised_bill for '
              'procedure '
              '45378","escalate_to":null,"line_dispositions":[{"procedure_code":"45378","disposition":"approved","amount":1150}],"approved_total":0,"refused_total":0,"evidence":["45378 '
              'requires itemised_bill","itemised_bill is missing"]}}'],
 'CLM-9014': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9014"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-6118"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-6118","procedure_code":"29881","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-6118","procedure_code":"29881","date_of_service":"2026-10-04"}}]}',
              '{"type":"final","final":{"decision":"request_document","trigger":null,"missing":"a current '
              'pre-authorisation for procedure '
              '29881","escalate_to":null,"line_dispositions":[{"procedure_code":"29881","disposition":"approved","amount":1950}],"approved_total":0,"refused_total":0,"evidence":["PA-5640 '
              'found","PA-5640 expired on 2026-05-31","date of service is 2026-10-04"]}}'],
 'CLM-9015': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9015"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}}]}',
              '{"type":"action_block","reasoning_summary":"Check the complete claim against prior decided '
              'claims.","actions":[{"call_id":"t03-c01","tool":"check_duplicate_claim","args":{"member_id":"M-5502","hospital_id":"H-114","date_of_service":"2026-10-05","lines":[{"code":"99213","amount":200}]}}]}',
              '{"type":"final","final":{"decision":"escalate","trigger":"DUPLICATE_CLAIM","missing":null,"escalate_to":"human '
              'claims assessor","line_dispositions":[],"approved_total":0,"refused_total":0,"evidence":["prior claim '
              'CLM-8715","matched member_id, hospital_id, date_of_service, and complete lines"]}}'],
 'CLM-9061': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9061"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9061","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180,"refused_total":0,"evidence":["line '
              '99213 is covered","approved_total 180","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180}],"approved_total":180,"refused_total":0,"evidence":["line '
              '99213 is covered","approved_total 180","refused_total 0"]}}'],
 'CLM-9062': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9062"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-3390"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"80053","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9062","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"80053","disposition":"approved","amount":90}],"approved_total":90,"refused_total":0,"evidence":["line '
              '80053 is covered","approved_total 90","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"80053","disposition":"approved","amount":90}],"approved_total":90,"refused_total":0,"evidence":["line '
              '80053 is covered","approved_total 90","refused_total 0"]}}'],
 'CLM-9063': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9063"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-6118"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-330"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-6118","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9063","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":200}],"approved_total":200,"refused_total":0,"evidence":["H-330 '
              'is non-panel","approved_total 200","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":200}],"approved_total":200,"refused_total":0,"evidence":["H-330 '
              'is non-panel","approved_total 200","refused_total 0"]}}'],
 'CLM-9064': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9064"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-5502"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-5502","procedure_code":"27447","attached_documents":["itemised_bill","discharge_summary"]}}]}',
              '{"type":"action_block","reasoning_summary":"Check required pre-authorisation '
              'evidence.","actions":[{"call_id":"t03-c01","tool":"get_preauthorisation","args":{"member_id":"M-5502","procedure_code":"27447","date_of_service":"2026-10-26"}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t04-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9064","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"27447","disposition":"approved","amount":5000,"preauthorisation_id":"PA-5702"}],"approved_total":5000,"refused_total":0,"evidence":["line '
              '27447 is covered","PA-5702 cited for line 27447","PA-5702 is valid on 2026-10-26","approved_total '
              '5000","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"27447","disposition":"approved","amount":5000,"preauthorisation_id":"PA-5702"}],"approved_total":5000,"refused_total":0,"evidence":["line '
              '27447 is covered","PA-5702 cited for line 27447","PA-5702 is valid on 2026-10-26","approved_total '
              '5000","refused_total 0"]}}'],
 'CLM-9065': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9065"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-2214"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-114"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"47120","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-2214","procedure_code":"70553","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9065","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1400},{"procedure_code":"70553","disposition":"approved","amount":500}],"approved_total":1900,"refused_total":0,"evidence":["a '
              'disposition for both lines","47120 covered for 1400","70553 covered for 500","approved_total '
              '1900","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"47120","disposition":"approved","amount":1400},{"procedure_code":"70553","disposition":"approved","amount":500}],"approved_total":1900,"refused_total":0,"evidence":["a '
              'disposition for both lines","47120 covered for 1400","70553 covered for 500","approved_total '
              '1900","refused_total 0"]}}'],
 'CLM-9066': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9066"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-6118"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-207"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-6118","procedure_code":"99213","attached_documents":["itemised_bill"]}},{"call_id":"t02-c04","tool":"check_coverage","args":{"member_id":"M-6118","procedure_code":"70553","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9066","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"70553","disposition":"approved","amount":620}],"approved_total":800,"refused_total":0,"evidence":["a '
              'disposition for both lines","99213 covered for 180","70553 covered for 620","approved_total '
              '800","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":180},{"procedure_code":"70553","disposition":"approved","amount":620}],"approved_total":800,"refused_total":0,"evidence":["a '
              'disposition for both lines","99213 covered for 180","70553 covered for 620","approved_total '
              '800","refused_total 0"]}}'],
 'CLM-9067': ['{"type":"action_block","reasoning_summary":"Retrieve claim '
              'facts.","actions":[{"call_id":"t01-c01","tool":"get_claim","args":{"case_id":"CLM-9067"}}]}',
              '{"type":"action_block","reasoning_summary":"Run independent checks required for the '
              'decision.","actions":[{"call_id":"t02-c01","tool":"lookup_policy","args":{"member_id":"M-3390"}},{"call_id":"t02-c02","tool":"get_hospital_status","args":{"hospital_id":"H-330"}},{"call_id":"t02-c03","tool":"check_coverage","args":{"member_id":"M-3390","procedure_code":"99213","attached_documents":["itemised_bill"]}}]}',
              '{"type":"action_block","reasoning_summary":"All required facts are resolved; issue the gated decision '
              'letter.","actions":[{"call_id":"t03-c01","tool":"issue_decision_letter","args":{"case_id":"CLM-9067","decision_record":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":250}],"approved_total":250,"refused_total":0,"evidence":["H-330 '
              'is non-panel","99213 is covered for 250","approved_total 250","refused_total 0"]}}}]}',
              '{"type":"final","final":{"decision":"approve_in_principle","trigger":null,"missing":null,"escalate_to":null,"line_dispositions":[{"procedure_code":"99213","disposition":"approved","amount":250}],"approved_total":250,"refused_total":0,"evidence":["H-330 '
              'is non-panel","99213 is covered for 250","approved_total 250","refused_total 0"]}}']}
