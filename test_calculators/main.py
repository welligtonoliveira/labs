from calculators.proposal_calculator import ProposalCalculator
import json
from datetime import datetime

def main():
    data_param_proposal_calculator = {
        "amount": 1500.00,
        "period": 6,
        "payday": 5,
        "initial_date": datetime.now().date(),
        "interest_rate": 16.9,
        "agio_rate": 3.384,
        "tac_rate": 9.5,
        "extra_days": 10,
    }
        
    calculator = ProposalCalculator(**data_param_proposal_calculator)
    proposal = calculator.all()
    
    def json_default(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    print(json.dumps(proposal, indent=4, ensure_ascii=False, default=json_default))

if __name__ == "__main__":
    main()

