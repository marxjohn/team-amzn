/**
 * Created by MaxGoovaerts and CJ on 2/8/2015.
 */

function getStopWords(array) {
    //format stopwords into array
    var str = array.replace("{","").replace("}","").split('\'').join('').split(',').join('');
    console.log(str);

    var cur = "";
    var words = [];
    for(i=0; i<str.length; i++) {
        if(str[i] == " ") {
            words.push(cur);
            cur = "";
        }
        else {
            cur += str[i];
        }

    }
    words.sort();

    //generate html
    var html = '<select id="stop_words_select" multiple="multiple" size=8>';
    for (var i = 0; i < words.length; i++) {
        html += '<option value="' + words[i] + '">' + words[i] + '</option>';
    }
    html += '</select>';
    console.log(html);

    //attach to html in page
    var el = document.getElementById("stop_words");
    el.innerHTML = html;
}

function deleteWords() {
    var words = document.getElementById("stop_words_select");
    var selected = [];
    for (var i = 0; i < words.length; i++) {
        if(words.options[i].selected) selected.push(words.options[i].value);
    }
    console.log(selected);
}
