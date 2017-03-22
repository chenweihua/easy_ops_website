draw2d.shape.node.WorkFlowBaseImage = draw2d.shape.basic.Image.extend({
	Name: "图象基类",
	Cname:"图象基类。。。",	
	init: function(sImgId,width,height){
		this._super({//此处必须传object
			'path':"/static/images/my_draw2d/" + sImgId + ".png",
			'width':width,
			'height':height
		});
	}
});