/**
 * Created by cse498 on 3/29/15.
 */
$(document).ready(function () {
    $(".settings").hover(function () {
                             $("#hoverDropDown").toggle();
                            $(".settings").toggleClass("focus_link");
                         }

    );
});