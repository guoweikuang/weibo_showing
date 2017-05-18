class Solution:
    # @return a boolean
    def isMatch(self, s, p):
        if len(p) == 0:
            return len(s) == 0
        if len(p) == 1 or p[1] != '*':
            if len(s) == 0 or (s[0] != p[0] and p[0] != '.'):
                return False
            return self.isMatch(s[1:], p[1:])
        else:
            i = -1
            length = len(s)
            while i < length and (i < 0 or p[0] == '.' or p[0] == s[i]):
                if self.isMatch(s[i + 1:], p[2:]):
                    return True
                i += 1
            return False


def caluate_difficult():
    a = 1
    b = 34
    a_bin = bin(a)[2:]
    b_bin = bin(b)[2:]
    if a < b:
        cha = len(b_bin) - len(a_bin)
        a_bin = '0' * cha + a_bin
    else:
        cha = len(a_bin) - len(b_bin)
        b_bin = '0' * cha + b_bin
    print a_bin
    print b_bin
    number = 0
    for i, j in zip(a_bin, b_bin):
        if i != j:
            number += 1
    print(number)


def fizz_buzz(n):
    guo = ['Fizz' * (not x % 3) + 'Buzz' * (not x % 5) or str(x) for x in range(1, n + 1)]
    print guo

    get_list = []
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            get_list.append('FizzBuzz')
        elif i % 3 == 0:
            get_list.append('Fizz')
        elif i % 5 == 0:
            get_list.append('Buzz')
        else:
            get_list.append(str(i))
    print get_list


if __name__ == '__main__':
    solution = Solution()
    print(solution.isMatch('aaa', 'a*'))
    fizz_buzz(15)