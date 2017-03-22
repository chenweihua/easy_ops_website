draw2d.shape.node.FlowCircle = draw2d.shape.basic.Circle.extend({
	NAME:"circle",
	init: function(){
		this._super();
		this.setResizeable(false);		
	},
});