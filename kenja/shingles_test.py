from kenja.shingles import split_to_str
from kenja.shingles import create_two_shingles
from kenja.shingles import tokenize
from kenja.shingles import tokenizer
from kenja.shingles import calculate_similarity
from nose.tools import raises


def for_split_to_str(test_data, estimated_words):
    result = split_to_str(test_data)
    assert result.pop(0) == 'code'
    texts = []
    nums = []
    while result:
        nums.append(result.pop(0))
        texts.append(result.pop(0))

    for ew, w in zip(estimated_words, texts):
        assert ew == w


def get_shingles_str(shingles):
    return set([(shingle[1], shingle[3]) for shingle in shingles])


def check_torknized_str(torknized_result, estimated_result):
    torknized_result = torknized_result[1:]
    for result, estimated in zip(torknized_result, estimated_result):
        if result[2] != estimated:
            return False
    return True


def test_split_to_str():
    test_data = "public void main()"
    print("[test]", test_data)
    estimated_result = ['public', ' ', 'void', ' ', 'main', '(', ')']
    for_split_to_str(test_data, estimated_result)

    test_data = '""'
    print("[test]", test_data)
    estimated_result = ['""']
    for_split_to_str(test_data, estimated_result)

    test_data = r'"\""'
    print("[test]", test_data)
    estimated_result = [r'"\""']
    for_split_to_str(test_data, estimated_result)
    print("[test]", test_data)

    test_data = "''"
    print("[test]", test_data)
    estimated_result = ["''"]  # ''
    for_split_to_str(test_data, estimated_result)

    test_data = r"'\"'"
    print("[test]", test_data)
    estimated_result = [r"'\"'"]  # '\"'
    for_split_to_str(test_data, estimated_result)

    test_data = r'"\'"'
    print("[test]", test_data)
    estimated_result = [r'"\'"']  # '\"'
    for_split_to_str(test_data, estimated_result)

    test_data = r'"\n"'
    print("[test]", test_data)
    estimated_result = [r'"\n"']  # "\n"
    for_split_to_str(test_data, estimated_result)

    test_data = r"'\n'"
    print("[test]", test_data)
    estimated_result = [r"'\n'"]  # '\n'
    for_split_to_str(test_data, estimated_result)


def test_create_two_shingles():
    seq = tokenize(tokenizer, "public void main()")[1:]
    result = get_shingles_str(create_two_shingles(seq))
    estimated_result = {('public', 'void'), ('void', 'main'), ('main', '('), ('(', ')')}
    assert result == estimated_result
    seq = tokenize(tokenizer, "public int main()")[1:]
    result = get_shingles_str(create_two_shingles(seq))
    estimated_result = {('public', 'int'), ('int', 'main'), ('main', '('), ('(', ')')}
    assert result == estimated_result


def test_tokenize():
    result = tokenize(tokenizer, "public void main()")
    estimated_result = ['public', 'void', 'main', '(', ')']
    assert check_torknized_str(result, estimated_result)
    estimated_result = ['String', 'str', '=', r'"\""']
    result = tokenize(tokenizer, r'String str="\""')
    assert check_torknized_str(result, estimated_result)


def test_calculate_similarity():
    script1 = "public void main()"
    script2 = "public int main()"
    result = calculate_similarity(script1, script2)
    assert result == (1.0 / 3.0)


@raises(ZeroDivisionError)
def test_calculate_similarity2():
    script1 = ""
    script2 = ""
    calculate_similarity(script1, script2)
