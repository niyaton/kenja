from kenja.shingles import split_to_str
from kenja.shingles import create_two_shingles
from kenja.shingles import tokenize
from kenja.shingles import tokenizer
from kenja.shingles import calculate_similarity

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

def test_split_to_str():
    test_data = "public void main()"
    estimated_result = ['public', ' ', 'void', ' ', 'main', '(', ')']
    for_split_to_str(test_data, estimated_result)
    test_data = '""'
    estimated_result = ['""']
    for_split_to_str(test_data, estimated_result)
    test_data = r'"\""'
    estimated_result = [r'"\""']
    for_split_to_str(test_data, estimated_result)
    test_data = "''"
    estimated_result = ["''"]
    for_split_to_str(test_data, estimated_result)

def test_create_two_shingles():
    seq = tokenize(tokenizer, "public void main()")[1:]
    result = create_two_shingles(seq)
    seq = tokenize(tokenizer, "public int main()")[1:]
    result = create_two_shingles(seq)
    assert False == result

def test_tokenize():
    result = tokenize(tokenizer, "public void main()")
    result = tokenize(tokenizer, r'String str="\""')
    assert False == result

def test_calculate_similarity():
    script1 = "public void main()"
    script2 = "public int main()"
    result = calculate_similarity(script1, script2)
    assert result == (1.0 / 3.0)
