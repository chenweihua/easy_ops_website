//test demo


function D_1(){
	/*
	普通图形需要在外部add，文本需要在modal展示完成后add到canvas上。
	*/
	canvas.add( new draw2d.shape.basic.Oval(),100,100);

	$("#id_modal_common").on('shown.bs.modal',function(){
		console.log("test");
		var msg = new draw2d.shape.note.PostIt({text:"Add input and output ports at any position of the \nshape via generic API calls."});

		canvas.add(msg);
	});
	$("#id_modal_common").modal();
}