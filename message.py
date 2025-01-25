import os


def is_updated(message: str, path: str) -> bool:
    """ pathというファイルに保存されたmessageと比較して
    messageが新しければ、messageをpathというファイルに保存してTrueを返す。
    messageが古ければ、Falseを返す。
    副作用として、pathに指定したファイルへのIOが発生する。

    main.is_message_updated()より一般化した
    """
    try:
        # ファイルが存在しない場合
        if not os.path.exists(path):
            try:
                # ディレクトリが存在しない場合は作成
                os.makedirs(os.path.dirname(path), exist_ok=True)

                # 新規ファイルに書き込み
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(message)
                return True
            except Exception as e:
                raise IOError(f"ファイル作成中にエラーが発生しました: {e}")
        # ファイルが存在する場合、内容を読み込む
        with open(path, 'r', encoding='utf-8') as f:
            old_message = f.read()
        # メッセージが異なる場合
        if message != old_message:
            # ファイルを更新
            with open(path, 'w', encoding='utf-8') as f:
                f.write(message)
            return True
        # メッセージが同じ場合
        return False
    except PermissionError:
        raise PermissionError(f"ファイル {path} にアクセス権限がありません。")
    except IOError as e:
        raise IOError(f"ファイル操作中にIOエラーが発生しました: {e}")
    except Exception as e:
        raise Exception(f"予期せぬエラーが発生しました: {e}")
