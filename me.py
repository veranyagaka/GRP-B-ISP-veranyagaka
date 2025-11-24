s = input()

arr = [int(x) for x in s.split()]
arr.sort()

if max(arr) - min(arr) >= 10:
    print("check again")
else:
    print("final", arr[1])