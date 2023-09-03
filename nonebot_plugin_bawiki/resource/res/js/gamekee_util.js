() => {
  /**
   * @param {string} selector
   * @param {(obj: HTMLElement) => any} callback
   */
  const executeIfExist = (selector, callback) => {
    const obj = document.querySelector(selector);
    if (obj) callback(obj);
  };

  // 给内容加上 padding
  executeIfExist('div.wiki-detail-body', (obj) => (obj.style.padding = '20px'));

  // 隐藏 Header 避免遮挡页面
  executeIfExist('div.wiki-header', (obj) => (obj.style.display = 'none'));

  // 隐藏关注按钮
  executeIfExist(
    'div.user-box > button',
    (obj) => (obj.style.display = 'none')
  );

  // 删掉视频播放器
  for (const it of document.querySelectorAll('div.video-play-wrapper'))
    it.remove();

  // 展开所有选项卡内容
  for (const it of document.querySelectorAll('div.slide-item'))
    it.classList.add('active');

  // 删掉点赞和收藏按钮
  executeIfExist('div.article-options', (obj) => obj.remove());

  // 删掉底部边距
  executeIfExist(
    'div.wiki-detail-body',
    (obj) => (obj.style.marginBottom = '0')
  );
};
