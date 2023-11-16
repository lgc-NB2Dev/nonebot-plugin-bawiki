() => {
  // #region util functions
  /**
   * @param {string} selector
   * @param {number} val，设为 max 留空（undefined, null）或填 0
   */
  const setProgress = (selector, val) => {
    const obj = $(selector);
    if (!obj.is('input[type="range"]')) {
      console.warn(`utilStuSetProgress: invalid selector "${selector}"`);
      return;
    }
    const min = Number(obj.attr('min')) || 1;
    const max = Number(obj.attr('max')) || 1;
    const willSet =
      typeof val === 'number' && val >= min && val <= max ? val : max;
    obj.val(willSet).trigger('input');
  };
  // #endregion

  // 切换中文
  if (localStorage.getItem('language') !== 'Cn') changeLanguage('Cn');

  // #region 关闭更新日志
  const changeLogModelElem = $('#modal-changelog');
  if (changeLogModelElem.is(':visible')) {
    changeLogModelElem.remove();
    $('.modal-backdrop').remove();
    localStorage.setItem('changelog_seen', '1145141919810');
  }
  // #endregion

  // #region 进度条拉最大
  setProgress('#ba-statpreview-levelrange');
  setProgress('#ba-skillpreview-exrange');
  setProgress('#ba-skillpreview-range');
  setProgress('#ba-weaponpreview-levelrange');
  setProgress('#ba-weapon-skillpreview-range');
  setProgress('#ba-gear-skillpreview-range');
  // #endregion

  // #region 展开所有项目
  const cardHeaderElem = $('.card-header');
  // 我自己的 schale db 镜像已经执行过下面的操作了，当未找到 card-header 时不再执行
  if (cardHeaderElem.length !== 0) {
    const cardBodyElem = $('.card-body');
    const stuPageChildren = cardBodyElem.children('.tab-content').children();

    // 获取 nav bar 后移除
    const navElem = cardHeaderElem.children('nav#ba-item-list-tabs');
    navElem.children().removeClass('active');
    navElem.remove();

    // 移动 card-header 中元素到 card-body 后移除 card header
    const headerChildren = cardHeaderElem.children();
    cardBodyElem.prepend(headerChildren);
    cardHeaderElem.remove();

    // 将 nav bar 添加到各 page 头部，删除 nav 中不可见的对应 page
    stuPageChildren.each((_, elem) => {
      const navClone = navElem.clone();
      $(elem).prepend(navClone);
      elem.classList.add('show', 'active');

      const pageName = elem.id.replace('ba-student-page-', '');
      const tabElem = navClone.children(`#ba-student-tab-${pageName}`);
      if (!tabElem.is(':visible')) {
        elem.remove();
        return;
      }
      tabElem.addClass('active');
    });
  }
  // #endregion

  // 背景填满截图
  $('#ba-background').css('height', document.body.scrollHeight);
};
