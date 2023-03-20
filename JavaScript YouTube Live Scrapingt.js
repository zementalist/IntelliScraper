function autoScrapeYT(){
let reached_to_bottom = false;
let interval_number = 0;
let patience = 10;
const delay = ms => new Promise(res => setTimeout(res, ms));

async function scrollToBottom(){
    document.querySelector("video").pause();
    const scrollingElement = (document.scrollingElement || document.body);
	let old_scroll = scrollingElement.scrollHeight;
scrollingElement.scrollTop = scrollingElement.scrollHeight -5;
    await delay(1000);
	let new_scroll =scrollingElement.scrollHeight;
    reached_to_bottom = old_scroll == new_scroll;

    
if(reached_to_bottom){
    patience -= 1;
    reached_to_bottom = false;
    if(patience < 1){
    clearInterval(interval_number);
    let description = document.querySelector("#description-inline-expander").innerText
    l = document.querySelectorAll(".style-scope ytd-comment-renderer #content #content-text")
    comments = Array.from(l).map(item => {return item.innerText})
    comments
    let jsondata = {"description":description, "comments":comments};
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(jsondata));
    var dlAnchorElem = document.querySelector('a');
    dlAnchorElem.setAttribute("href",     dataStr     );
    dlAnchorElem.setAttribute("download", "scene.json");
    dlAnchorElem.click();
    document.querySelector(".ytp-next-button.ytp-button").click();
    await delay(5000);
    autoScrapeYT();
    }
}
}

interval_number = setInterval(scrollToBottom, 500)
}
autoScrapeYT()
