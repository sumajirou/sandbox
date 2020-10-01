#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 参考URL
# https://www.swetake.com/qrcode/qr1.html

# コマンドラインで出力すると黒背景の場合が多い．QRコードはソフトによるがネガポジ反転すると認識されないことが多い．
# もちろん色反転オプションは付ける．

# QRコードのフォーマットは文字列で表す．末尾の改行あり．例↓
"""111111
1000001
1011101
1011101
1011101
1000001
1111111
"""

import reedsolo
import re
import random


def main():
    # 入力データ
    input_data = "ABCDE123"
    print("input_data:", input_data)

    qrstr = qr_encode(input_data)
    qrstr = add_padding(qrstr)
    print_qrstr(qrstr)


def print_qrstr(qrstr):
    """
    QRコードを出力する
    """
    # U+2588	█	Full block
    table = str.maketrans({'0': '██', '1': '  ', '2': '22', '3': '33'})
    qrstr = qrstr.translate(table)
    print(qrstr)


def add_padding(qrstr):
    """
    上下左右に余白を4マスずつ追加する
    """
    lines = qrstr.split('\n')[:-1]
    lines = [f'0000{line}0000' for line in lines]
    padding_line = '0' * len(lines[0])
    lines = [padding_line] * 4 + lines + [padding_line] * 4
    qrstr = '\n'.join(lines) + '\n'
    return qrstr


def nbin(num, n=0):
    """
    numをn桁でゼロ埋めした2進数に変換する．
    nを指定しなかった場合は0埋めしない．
    """
    return format(num, f'0{n}b')


def xor_bin(x, y, n=0):
    """
    2進数文字列xとyのxorを計算し，n桁でゼロ埋めした2進数文字列で返す．
    nを指定しなかった場合はゼロ埋めしない．
    """
    return nbin(int(x, 2) ^ int(y, 2), n)


def convert_char_to_bin(chars):
    """
    2文字ないし1文字を2進数に変換する関数
    """
    table = {
        "0":  0, "1":  1, "2":  2, "3":  3, "4":  4, "5":  5, "6":  6, "7":  7, "8":  8, "9":  9,
        "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17, "I": 18, "J": 19,
        "K": 20, "L": 21, "M": 22, "N": 23, "O": 24, "P": 25, "Q": 26, "R": 27, "S": 28, "T": 29,
        "U": 30, "V": 31, "W": 32, "X": 33, "Y": 34, "Z": 35, " ": 36, "$": 37, "%": 38, "*": 39,
        "+": 40, "-": 41, ".": 42, "/": 43, ":": 44,
    }
    if len(chars) == 2:
        num = table[chars[0]] * 45 + table[chars[1]]
        return nbin(num, 11)
    else:
        num = table[chars]
        return nbin(num, 6)


def convert_str_to_matrix(buf):
    """
    QRコード文字列をmatrixに変換する
    """
    lines = buf.split('\n')[:-1]
    matrix = [list(line) for line in lines]
    return matrix


def convert_matrix_to_str(matrix):
    """
    QRコードmatrixを文字列に変換する
    """
    lines = [''.join(line) for line in matrix]
    buf = '\n'.join(lines) + '\n'
    return buf


def bch15_5(x):
    """
    5桁の2進数を受け取り，BCH(15,5)を計算した結果を2進数で返す
    """
    g = '10100110111'
    f = x + '0' * 10
    while int(f, 2) >= int(g, 2):
        h = g + '0' * (len(f) - len(g))
        f = xor_bin(f, h)
    return nbin(int(f, 2), 10)


def qr_encode(input_data):
    """
    入力された文字列をQRコード化する
    フォーマットは英数字モード・バージョン1・誤り訂正レベルH・マスクパターン011で固定
    """
    input_data_len = len(input_data)
    # モード指示子 英数字モードは0010
    mode = '0010'
    print("mode:", mode)

    # 誤り訂正レベル H (30%)
    error_correction_level = '10'

    # 文字数指示子 英数字モードは9bitで文字数を表す
    character_count = nbin(input_data_len, 9)
    print("character_count:", character_count)

    # 英数字モードでは変換表を使って2文字ずつ11bitに変換する．1文字余った場合6bitに変換する．
    # 入力値を2文字ずつ分割
    data = re.split('(..)', input_data)
    data = [x for x in data if x]  # => ['AB', 'CD', 'E1', '23']
    print("data:", data)

    # 変換表を使って2進数に変換
    data = ''.join(map(convert_char_to_bin,  data))
    print("data:", data)

    # コード語変換
    data = mode + character_count + data + '0000'
    print("data:", data)

    # 8の倍数になるようbitを付加する
    bit_padding_len = (8 - len(data) % 8) % 8
    data = data + '0' * bit_padding_len
    print("data:", data)

    # シンボルのデータコード数になるまで11101100 および 00010001を交互に付加する
    data_code_words = 9
    word_padding_len = data_code_words - len(data) / 8
    while word_padding_len >= 2:
        data = data + '1110110000010001'
        word_padding_len -= 2
    if word_padding_len == 1:
        data = data + '11101100'
    print("data:", data)

    # 8bit毎にintに変換
    data = [int(x, 2) for x in re.split('(.{8})', data) if x]
    # =>  [32,65,205,69,41,220,46,128,236]
    print("data:", data)

    # 誤り訂正シンボル数17のリード・ソロモン符号で誤り訂正シンボルを付加
    rsc = reedsolo.RSCodec(17)
    data = list(rsc.encode(data))
    print("data:", data)

    # 2進化
    data = ''.join([nbin(x, 8) for x in data])
    print("data:", data)

    # バージョン1のQRコードのベース
    # 0:白
    # 1:黒
    # 2:形式情報
    # 3:データ・誤り訂正コード
    qrstr = """\
111111102333301111111
100000102333301000001
101110102333301011101
101110102333301011101
101110102333301011101
100000102333301000001
111111101010101111111
000000002333300000000
222222122333322222222
333333033333333333333
333333133333333333333
333333033333333333333
333333133333333333333
000000001333333333333
111111102333333333333
100000102333333333333
101110102333333333333
101110102333333333333
101110102333333333333
100000102333333333333
111111102333333333333
"""
    # QRコード本体
    matrix = convert_str_to_matrix(qrstr)

    # QRコードの骨格
    base_matrix = convert_str_to_matrix(qrstr)

    # データコード部にデータを挿入する
    # matrixの座標
    x, y = 20, 20
    direction = -1  # 1は下向きに，-1は上向きに進む
    pos = 'right'  # または'left'．挿入箇所の列に対する相対位置

    # dataのindex
    i = 0
    # (x,y)がデータコード部ならデータを入れてiを1すすめる．dataの長さだけ繰り返すと挿入が完了する．
    while i < len(data):
        if matrix[y][x] == '3':
            # データコード部なら挿入
            matrix[y][x] = data[i]
            i += 1

        if pos == 'right':
            # 右側のときは左側に移動
            pos = 'left'
            x -= 1
            continue

        pos = 'right'
        if direction == -1 and y == 0:
            # 上端の時は左に移動し方向を下に
            x -= 1
            direction = 1
        elif direction == 1 and y == 20:
            # 下端の時は左に移動し方向を上に
            x -= 1
            direction = -1
        else:
            # どちらでもないときは右に移動し上か下に移動
            x += 1
            y += direction

        # 左から7列目の縦のタイミングパターンをスキップする
        if x == 6:
            x -= 1

    # マスクを8種類適用
    # マスクの評価
    # とりあえずマスクパターン011を選択	(i+j) mod 3 = 0
    mask_pattern = '011'
    for y in range(0, 21):
        for x in range(0, 21):
            # コード部のみ対象とする
            if base_matrix[y][x] == '3' and (x+y) % 3 == 0:
                # matrix[y][x] = {'0': '1', '1': '0'}[matrix[y][x]]  # 0と1を反転
                # matrix[y][x] = str(1 - int(matrix[y][x]))  # 0と1を反転
                matrix[y][x] = matrix[y][x].translate(
                    str.maketrans('01', '10'))  # 0と1を反転

    # 形式情報の作成
    # 誤り訂正ビットの計算
    error_correction_bit = bch15_5(error_correction_level + mask_pattern)
    print('error_correction_bit', error_correction_bit)

    format_info = error_correction_level + mask_pattern + error_correction_bit
    print('format_info', format_info)

    format_info = xor_bin(format_info, '101010000010010', 15)
    print('format_info', format_info)

    # 形式情報の挿入(横)
    matrix[8][0:6] = format_info[0:6]
    matrix[8][7] = format_info[7]
    matrix[8][-8:] = format_info[-8:]

    # 形式情報の挿入(縦) 一旦行列を転置してからやると楽
    matrix = list(map(list, zip(*matrix)))
    format_info = format_info[::-1]
    matrix[8][0:6] = format_info[0:6]
    matrix[8][7:9] = format_info[7:9]
    matrix[8][-7:] = format_info[-7:]
    format_info = format_info[::-1]
    matrix = list(map(list, zip(*matrix)))

    # matrixを文字列に戻す
    qrstr = convert_matrix_to_str(matrix)
    return qrstr


if __name__ == "__main__":
    main()


# おまけ

# 001000000100000111001101010001010010100111011100001011101000000011101100001010101001111101001010110111011111010010101001111011111001011010001010010001101110110101010101111000000110000001001010 11011011 00111101

#          0101
#          0010
#          0110
#          0101
#          1011
#          0011

#          1001
#          0111
# 101100 00111000001010
# 011111 00010101110011
# 100010 01110101011000
# 111010 10100101111011
#          100001000010
#          101010000100
#          101111000100
#          101111011010
#          111010011100
#          011100111000
#          001001011101
#          001101000000
