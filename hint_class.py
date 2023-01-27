
class Hint:
    def __init__(self, ans: str, hint_num: int=0):
        self.hint_num: int = hint_num
        self.ans: str = ans
        self.description = self.make_hint()

    def make_hint(self) -> str:
        match self.hint_num:
            case 0:
                return f"\nMASTERMIND: A hint?! Really?! You need a hint?! Fine. The last digit of the number in my head is {self.ans[-1]}"
            case 1:
                sum = 0
                for idx in range(len(self.ans)):
                    sum += int(self.ans[idx])
                return f"\nMASTERMIND: FINE. The sum of the digits for the number in my head is {sum}"
            case 2:
                less_than_equal_3_count = 0
                for idx in range(len(self.ans)):
                    if int(self.ans[idx]) <= 3:
                        less_than_equal_3_count += 1
                return f"\nMASTERMIND: There are {less_than_equal_3_count} digits in the number in my head that are less than or equal to 3"
            case 3:
                product = 1
                for idx in range(len(self.ans)):
                    product *= int(self.ans[idx])
                return f"\nMASTERMIND: FINE. The product of the digits for the number in my head is {product}"
            case 4:
                 while True:
                    hint = str(random.randint(0,7))
                    if hint not in self.ans:
                        return f"\nMASTERMIND: {hint} is not a digit in the number I am thinking of"
        return ""



