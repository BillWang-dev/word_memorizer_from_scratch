#!/bin/bash

# 英语单词记忆系统 - 发布脚本
# 自动创建GitHub Release触发多平台构建

if [ $# -eq 0 ]; then
  echo "用法: ./create-release.sh <版本号>"
  echo "示例: ./create-release.sh v1.0.0"
  exit 1
fi

VERSION=$1

echo "🚀 准备发布版本: $VERSION"
echo "================================"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
  echo "📝 发现未提交的更改，正在提交..."
  git add -A
  git commit -m "feat: 准备发布 $VERSION"

fi

# 创建标签
echo "🏷️  创建版本标签: $VERSION"
git tag $VERSION

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main
git push origin $VERSION

echo ""
echo "✅ 发布完成！"
