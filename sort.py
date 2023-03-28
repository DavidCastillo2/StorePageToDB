def compare(a, b, attribute):
    if attribute == "name":
        return a.name < b.name


def sort(items, attribute):
    mergeSort(items, attribute)  # MergeSort Time
    return items


def mergeSort(items, attribute):
    if len(items) > 1:
        mid = len(items) // 2  # Finding the mid of the array
        L = items[:mid]  # Dividing the array elements
        R = items[mid:]  # into 2 halves

        mergeSort(L, attribute)  # Sorting the first half
        mergeSort(R, attribute)  # Sorting the second half

        i = j = k = 0

        # Copy data to temp arrays L[] and R[]
        while i < len(L) and j < len(R):
            # if L[i] < R[j]:
            if compare(L[i], R[j], attribute):
                items[k] = L[i]
                i += 1
            else:
                items[k] = R[j]
                j += 1
            k += 1

        # Checking if any element was left
        while i < len(L):
            items[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            items[k] = R[j]
            j += 1
            k += 1


def findName(items, name):
    retVal = []
    for item in items:
        if item.name.find(name) != -1:
            retVal.append(item)
    return retVal


def findBrand(items, brand):
    retVal = []
    for i in items:
        for item in i.brand:
            if item.brand.find(brand) != -1:
                retVal.append(item)
    return retVal
