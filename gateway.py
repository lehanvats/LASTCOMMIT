"""
gateway.py — Central API Gateway
Routes /challenge/<use_case_id> → the correct agent instance.
Each use-case runs its own agent defined in challenges/<id>/agent.py
"""
