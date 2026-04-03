from classes.calculator import Calculator
from classes.validator import Validator

#dictionary
mode_list = {
    "1": "calculate half-life by one distance",
    "2": "calculate half-life by multiple distances"
}

print("\n-------This is GNA V1.2 (Georgi's Nuclear Assistant)-------\n")

data = Validator.validate_hand_or_file()

if data:
    hand_or_file_check = 'y'
else:
    hand_or_file_check = 'n'

while True:
    workmode = Validator.validate_workmode(mode_list, data)

    calculator = Calculator(data)
    #TODO: manage workmode
    if workmode == '1':
        calculator.get_halflife_by_single_distance(hand_or_file_check)
    
    elif workmode == '2':
        calculator.get_halflife_by_multiple_distances()
    

    cont = Validator.validate_yes_no(hand_or_file_check)

    if cont.lower() == 'n':
      break
    elif cont.lower() == 'y':
      continue


print("\n-------End of calculation-------")