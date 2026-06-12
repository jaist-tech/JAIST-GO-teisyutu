# JAIST-GO

# 開発環境
python=3.11
## 藤田の環境
uvというパッケージマネージャを使用。
uv.lock、pyproject.tomlはそのためのファイル

## flaskの立ち上げ方(デバッグモード)
### venvの場合
上から順に試す
1. flask --app app run --debug
2. python -m flask --app app run --debug
### uvの場合
1. uv run flask --app app run --debug

## db(map)のセットアップ
flaskサーバーを起動した状態で以下のコードを実行する
(個人でgoogle map apiを発行しているのでweb上の表示はその工程を挟まないとできない)

1. flask create-dbで初期のデータベースを作成
2. flask insert-sampleでsampleデータの挿入
3. flask show-dataで確認