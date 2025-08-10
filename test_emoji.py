import emoji

# 利用可能な関数を確認
print("利用可能な関数:")
print(dir(emoji))

# バージョンを確認
print(f"\nemojiライブラリのバージョン: {emoji.__version__}")

# 絵文字除去のテスト
test_text = "こんにちは！😊 #テスト"
print(f"\nテストテキスト: {test_text}")

# 各関数を試してみる
try:
    result1 = emoji.replace_emoji(test_text, replace='')
    print(f"replace_emoji: {result1}")
except AttributeError as e:
    print(f"replace_emoji エラー: {e}")

try:
    result2 = emoji.replace(test_text, '')
    print(f"replace: {result2}")
except AttributeError as e:
    print(f"replace エラー: {e}")

try:
    result3 = emoji.demojize(test_text)
    print(f"demojize: {result3}")
except AttributeError as e:
    print(f"demojize エラー: {e}")

try:
    result4 = emoji.get_emoji_regexp().sub('', test_text)
    print(f"get_emoji_regexp: {result4}")
except AttributeError as e:
    print(f"get_emoji_regexp エラー: {e}")
