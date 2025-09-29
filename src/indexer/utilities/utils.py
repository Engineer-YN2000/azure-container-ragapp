import os
import logging
from typing import List

# モジュール専用のロガーを取得
logger = logging.getLogger(__name__)


def save_chunks_to_file(
    chunks: List[str], original_filename: str, output_dir: str = "debug_outputs"
):
    """
    チャンク化されたテキストのリストを、読みやすい形式でテキストファイルに保存します。

    Args:
        chunks: チャンク化されたテキストのリスト。
        original_filename: 保存するファイル名の基になる元のファイル名。
        output_dir: 保存先のディレクトリ。
    """
    try:
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)

        # 元のファイル名から拡張子を除いた部分を取得
        base_filename = os.path.splitext(original_filename)[0]
        output_filename = f"{base_filename}_chunks.txt"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"--- Chunks for {original_filename} ---\n")
            f.write(f"Total chunks: {len(chunks)}\n\n")

            for i, chunk in enumerate(chunks):
                f.write(f"--- CHUNK {i+1}/{len(chunks)} ---\n")
                f.write(chunk)
                f.write("\n\n")

        logger.info(f"Successfully saved {len(chunks)} chunks to '{output_path}'")

    except Exception as e:
        logger.error(f"Failed to save chunks to file: {e}", exc_info=True)
