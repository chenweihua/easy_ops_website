'use strict';
/*
test by yss
20160128

*/

function CaBk(){
    console.log('done');    
}             


function CheckFn(){
    console.log('checkfn');
    
}

/*
console.log('Start');
setTimeout(CaBk,10000);
console.log('End');
*/

//操作h2
$('h2.h2_1').click(function(){
    alert('test');
});

$(function(){
    var $Spans = $('#divTest span');
    console.log($Spans.length);
    for(var i = 0;i < $Spans.length;i++){
        /*
        $Spans[i].onclick = function(){
            alert(i);            
        };
        */
        (function(num){
            $Spans[num].onclick = function(){
                alert(num);
            }            
        })(i);
    }
});




