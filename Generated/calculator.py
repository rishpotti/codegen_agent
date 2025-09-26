
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error! Division by zero."
    return x / y

def calculator():
    print("Welcome to the CLI Calculator!")
    while True:
        try:
            num1 = float(input("Enter first number: "))
            operator = input("Enter operator (+, -, *, /): ")
            num2 = float(input("Enter second number: "))

            if operator == '+':
                print("Result:", add(num1, num2))
            elif operator == '-':
                print("Result:", subtract(num1, num2))
            elif operator == '*':
                print("Result:", multiply(num1, num2))
            elif operator == '/':
                print("Result:", divide(num1, num2))
            else:
                print("Invalid operator. Please use +, -, *, or /.")
        except ValueError:
            print("Invalid input. Please enter numbers for calculations.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        another_calculation = input("Do you want to perform another calculation? (yes/no): ").lower()
        if another_calculation != 'yes':
            print("Thank you for using the calculator. Goodbye!")
            break

if __name__ == "__main__":
    calculator()
