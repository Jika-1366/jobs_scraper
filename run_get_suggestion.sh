#!/bin/bash

# カレントディレクトリを移動
cd /home/jika/Desktop/my_projects/jobs_scraper

# 必要に応じて.envを読み込む（もし使っている場合）
if [ -f .env ]; then
    source .env
fi

# Pythonスクリプトを実行
/home/jika/anaconda3/envs/my_agents/bin/python get_suggestion.py