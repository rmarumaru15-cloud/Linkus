# Linkus アプリケーション

このプロジェクトは、ユーザーが自身の暗号通貨アドレスを公開し、カスタマイズ可能な個人ページを作成するためのフルスタックDjangoアプリケーションです。トップページにはコミュニティ掲示板機能があり、ユーザーランキングも表示されます。

## 前提条件

*   Python 3.10+
*   PostgreSQL
*   Redis

## セットアップ手順

1.  **リポジトリをクローンします**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **仮想環境を作成して有効化します**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # Windowsの場合: venv\Scripts\activate
    ```

3.  **依存関係をインストールします**
    ```bash
    pip install -r requirements.txt
    ```

4.  **環境変数を設定します**
    `linkus_app.env` ファイルをコピーして、内容を編集してください。特に、データベース接続情報（`DATABASE_URL`）とAlchemyのAPIキー（`ALCHEMY_API_KEY`）を実際のものに置き換える必要があります。

    ```bash
    cp linkus_app.env .env
    ```
    次に`.env`ファイルを開き、以下の項目を編集します。
    ```
    DATABASE_URL='postgres://USER:PASSWORD@HOST:PORT/NAME'
    ALCHEMY_API_KEY='your_actual_alchemy_api_key'
    ```

5.  **データベースのマイグレーションを実行します**
    これにより、データベースに必要なテーブルが作成されます。
    ```bash
    python manage.py migrate
    ```

6.  **(オプション) 管理者ユーザーを作成します**
    ```bash
    python manage.py createsuperuser
    ```

## アプリケーションの起動

アプリケーションを完全に機能させるには、3つのプロセス（Django開発サーバー、Celeryワーカー、Celery Beatスケジューラー）を起動する必要があります。それぞれ別のターミナルで実行してください。

1.  **Django 開発サーバーの起動**
    ```bash
    python manage.py runserver
    ```
    アプリケーションは `http://127.0.0.1:8000/` でアクセス可能になります。

2.  **Celery ワーカーの起動**
    非同期タスク（ランキング計算など）を処理します。
    ```bash
    celery -A linkus_app worker -l info
    ```

3.  **Celery Beat スケジューラーの起動**
    定期的なタスク（1時間ごとのランキング更新など）をスケジュールします。
    ```bash
    celery -A linkus_app beat -l info
    ```
