$(document).ready(function () {
    $(".titleBox").css({
        'width': ($(".infoBox").outerWidth() + 'px')
    });

    var canPreviewWidth = $(".canBoxImg").width();
    var canPreviewHeight = $(".canBoxImg").height();
    console.log(canPreviewWidth);
    if (canPreviewWidth > canPreviewHeight) {
        $(".canBoxImg").css({
            'width': (canPreviewHeight + 'px'),
            'height': (canPreviewHeight + 'px')
        });
    } else {
        $(".canBoxImg").css({
            'width': (canPreviewWidth + 'px'),
            'height': (canPreviewWidth + 'px')
        });
    }

    if ((canPreviewWidth < 110) || (canPreviewHeight < 110)) {
        $(".canBoxImg").css({
            'width': '110px',
            'height': '110px'
        });
    }
});
