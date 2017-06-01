from colorama import Fore

def prompt_yes_no(msg: str) -> bool:
	while True:
		command = input(msg + ' ')
		if command.lower() == 'yes':
			return True
		elif command.lower() == 'no':
			return False
		else:
			print(Fore.RED + "Enter 'yes' or 'no'.")
