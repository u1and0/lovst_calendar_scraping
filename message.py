from typing import List
import os
import difflib


def get_old_message(path: str) -> str:
    try:
        # ファイルが存在する場合、内容を読み込む
        with open(path, 'r', encoding='utf-8') as f:
            msg = f.read()
    except PermissionError:
        raise PermissionError(f"ファイル {path} にアクセス権限がありません。")
    except IOError as e:
        raise IOError(f"ファイル操作中にIOエラーが発生しました: {e}")
    except Exception as e:
        raise Exception(f"予期せぬエラーが発生しました: {e}")
    return msg


def show_diff(message: str, path: str) -> str:
    """ pathというファイルに保存されたmessageと比較して
    messageが新しければ、messageをpathというファイルに保存して差分の文字列を返す
    messageが古ければ、からの文字列を返す
    副作用として、pathに指定したファイルへのIOが発生する。

    Params:
        - message: str - 予約をまとめた文字列
        - path: str - 過去のmessageを保存するファイルパス
    Returns: str - 差分の文字列
    Throws:
        - PermissionError: ファイル {path} にアクセス権限がありません。
        - IOError: ファイル操作中にIOエラーが発生しました
        - Exception: 予期せぬエラーが発生しました
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
                return "(新規作成)"  # 新規作成は全て新しいため差分がない
            except Exception as e:
                raise IOError(f"ファイル作成中にエラーが発生しました: {e}")

        old_message = get_old_message(path)
        # メッセージが同じ場合
        if message == old_message:
            return ""

        # 差分のリストを表示
        diff_list = get_diff_list(old_message, message)
        diff_str = "\n".join(diff_list)

        # メッセージが異なる場合ファイルを更新
        with open(path, 'w', encoding='utf-8') as f:
            f.write(message)
        return diff_str

    except PermissionError:
        raise PermissionError(f"ファイル {path} にアクセス権限がありません。")
    except IOError as e:
        raise IOError(f"ファイル操作中にIOエラーが発生しました: {e}")
    except Exception as e:
        raise Exception(f"予期せぬエラーが発生しました: {e}")


def get_diff_list(old_message: str, new_message: str) -> List[str]:
    """2つの文字列の差分のある行のみdiff表示する。
    Returns: list[str] 差分のリスト
    """
    differ = difflib.Differ()
    diff = differ.compare(old_message.splitlines(), new_message.splitlines())
    diff_list = [
        di for di in diff if di.startswith("+ ") or di.startswith("- ")
    ]
    return diff_list
