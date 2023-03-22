function autoScrapeYT(){
    let reached_to_bottom = false;
    let interval_number = 0;
    let patience = 10;
    let file_is_downloaded = false;
    const delay = ms => new Promise(res => setTimeout(res, ms));
    
    async function scrollToBottom(){
        document.querySelector("video").pause();
        const scrollingElement = (document.scrollingElement || document.body);
        let old_scroll = scrollingElement.scrollHeight;
    scrollingElement.scrollTop = scrollingElement.scrollHeight -20;
        await delay(1000);
        let new_scroll =scrollingElement.scrollHeight;
        reached_to_bottom = old_scroll == new_scroll;
        spinners = document.querySelectorAll("#spinner");
        spinner_is_active = spinners[spinners.length-1].hasAttribute("active");
    if(reached_to_bottom && !spinner_is_active && !file_is_downloaded){
        patience -= 1;
        reached_to_bottom = false;
            clearInterval(interval_number);   
        let description = document.querySelector("#description-inline-expander").innerText
        l = document.querySelectorAll(".style-scope ytd-comment-renderer #content #content-text")
        comments = Array.from(l).map(item => {return item.innerText})
        comments
        let jsondata = {"description":description, "comments":comments};
        var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(jsondata));
        var dlAnchorElem = document.querySelector('a');
        dlAnchorElem.setAttribute("href",     dataStr     );
        dlAnchorElem.setAttribute("download", "dataitem.json");
        dlAnchorElem.click();
            file_is_downloaded = true;
        document.querySelector(".ytp-next-button.ytp-button").click();
        await delay(5000);
        autoScrapeYT();
    }
    }
    
    interval_number = setInterval(scrollToBottom, 500)
    }
    autoScrapeYT()
