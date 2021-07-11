$(document).ready(function() {
    let url = "https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=3947e3d5d8b546609feec4a6ee3951a8"

    $.ajax({
        url: url,
        method: "GET",
        dataType: "JSON",

        beforeSend: function() {
            $(".progress").show();
        },

        complete: function() {
            $(".progress").hide();
        },

        success: function(news) {
            let output = "";
            let latestNews = news.articles

            for (var i in latestNews) {
                output += `
            <div class="col l4 m6 s12">
            <h6>${latestNews[i].title}</h6>
            <div class="card medium hoverable">
              <div class="card-image">
                <img style="height: auto; width:auto;" src= "${latestNews[i].urlToImage}" class = "responsive-img"
                alt = "${latestNews[i].urlToImage}" >
              </div>

              <div class="card-content">
              <span class="card-title activator"><i class="material-icons right"></i></span>
              <h6 class="truncate">
              <p><b>News source</b>: ${latestNews[i].source.name} </p>
              <p><b>Published Date</b>: ${latestNews[i].publishedAt} </p>
            </div>
            <div class="card-reveal">
              <span class="card-title"><i class="material-icons right">close</i></span>
              < p> <b> Description </b>: ${latestNews[i].description}</>
            </div>
            <div class="card-action">
              <a href="${latestNews[i].url}" target="_blank" class="btn">Read More</a>
            </div>

             </div>
            </div> `;
            } //for loop

            if (output !== "") {
                $("#newsResults").html(output);
            }
        }, //success funtion

        error: function() {
            let errorMsg = `<div class="errorMsg center">Some error occured</div>`;
            $("#newsResults").html(errorMsg);
        },
    });
});