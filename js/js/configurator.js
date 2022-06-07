import { LCSerial, LCSerialCommandError } from "./lcserial.js";

var lcSerial = null;
var config = null;
var section_id_counter = 0;

class ConfigControl {
    constructor (input, path, name) {
        this.input = input;
        this.path = path;
        this.name = name
        $(input).on("change.real", () => this.saveValue());
    }

    loadValue(config) {
        var p = config;
        if (this.path) {
            const match = this.path.match(/^([^[]+)\[(\d+)\]$/);
            if (match) {
                console.log(match[1]);
                console.log(match[2]);
                p = config[match[1]][match[2]];
            }
        }
        const value = p[this.name];
        console.log(this.name + ": " + value);
        this.input.val(value).trigger("change.ui");
    }

    saveValue() {
        const val = this.input.val();
        var p = '';
        if (this.path) {
            const match = this.path.match(/^([^[]+)\[(\d+)\]$/);
            if (match) {
                p = match[1] + '/' + match[2] + '/';
            }
        }
        p += this.name;
        console.log(p);
        lcSerial.doCommand("SET " + p + " " + val);
    }
}

function configItemHTML(container, item, control) {
    //const itemDiv = $("<div></div>")
    //    .addClass("config-item")
    //    .appendTo(container);
    $("<div></div>")
        .addClass("title")
        .text(item.title)
        .appendTo(container);

    const detailsDiv = $("<div></div>")
        .addClass("details")
        .appendTo(container);

    detailsDiv.append(control);

    if (item.description.startsWith('<')) {
        $(item.description).appendTo(detailsDiv);
    } else {
        $("<p>" + item.description + "</p>").appendTo(detailsDiv);
    }
}

function addConfigLightLevelAdjust(container, item, level, config_path) {

    const value = $("<span></span>").addClass("range-value");

    var dragging = false;
    const input = 
        $("<input max='100' min='0' type='range'></input>")
        .on("input", () => { value.text(input.val()); lcSerial.doCommand("ON " + item.light + " " + input.val()); dragging = true })
        .on("mouseup", () => { if (dragging) { lcSerial.doCommand("OFF " + item.light); dragging = false; console.log("done"); }} )
        .on("change.ui", () =>  { value.text(input.val()); console.log("change.ui") });

    const control = $("<div></div>")
        .append(input)
        .append(value);

    configItemHTML(container, item, control);

    return new ConfigControl(input, config_path, item.name)
}

function addConfigLevelAdjust(container, item, config_path) {
    const value = $("<span></span>").addClass("range-value");

    var dragging = false;
    const units = item.units ? " " + item.units : "";
    const input = 
        $("<input min='0' type='range'></input>")
        .attr('max', item.max !== undefined ? item.max : 100)
        .attr('min', item.min !== undefined ? item.min : 0)
        .on("input", () => value.text(input.val() + units))
        .on("change.ui", () =>  value.text(input.val() + units));

    const control = $("<div></div>")
        .append(input)
        .append(value);

    configItemHTML(container, item, control);

    return new ConfigControl(input, config_path, item.name)

}

function addConfigMultiSelect(container, item, level, config_path) {

    const input = $("<select></select>");
    for (const value of item.values) {
        $("<option></option>")
            .attr('value', value)
            .text(item.labels[value])
            .appendTo(input);
    }
    configItemHTML(container, item, input);

    return new ConfigControl(input, config_path, item.name)
}

function addConfigSubMenu(submenu, level, config_path) {
    var controls = [];
    const section_id = "section-" + section_id_counter++;
    if (level > 0) {
        const div = $("<div></div>")
            .addClass("nav-item")
            .addClass("indent-" + level)
            .text(submenu.title)
            .data("section-id", section_id)
            .click(() => selectSection(section_id))
            .appendTo($(".nav-tree"));
        if (submenu.light !== undefined) {
            div.on("mouseenter", () => lcSerial.doCommand("ON " + submenu.light + " 100"));
            div.on("mouseleave", () => lcSerial.doCommand("OFF " + submenu.light));
        }
    }
    const section = $("<div></div>", {"class": "section", "id": section_id}).appendTo("div.body");
    $("<h1></h1>")
        .text(submenu.title)
        .appendTo(section);
    const container = $("<div></div>", {"class": "config-controls"}).appendTo(section);
    submenu.items.forEach((item) => {
        if (item.type == 'section') {
            controls = controls.concat(addConfigSubMenu(item, level + 1, submenu.config_path));
        }
        else if (item.type == 'light_level') {
            controls.push(addConfigLightLevelAdjust(container, item, level + 1, submenu.config_path));
        }
        else if (item.type == 'level') {
            controls.push(addConfigLevelAdjust(container, item, submenu.config_path));
        }
        else if (item.type == 'multi_select') {
            controls.push(addConfigMultiSelect(container, item, level + 1, submenu.config_path));
        }
    })
    return controls;
}

function selectFirstSection() {
    selectSection($("div.nav-tree .nav-item:first").data("section-id"));
}

function selectSection(sectionId) {
    $("div.section")
        .hide()
        .filter('#' + sectionId)
        .show();
    $("div.nav-tree .nav-item")
        .removeClass("selected")
        .filter((i,e) => $(e).data('section-id') == sectionId)
        .addClass("selected");
}

function buildConfigMenu(spec) {
    const container = $("div#config");
    container.empty();
    $(".nav-tree").empty();
    return addConfigSubMenu(spec, 0);
}

function loadConfigValues(controls, config) {
    for (const c of controls) {
        c.loadValue(config);
    }
}

async function saveConfig() {
    console.log("Saving");
    try {
        await lcSerial.doCommand("SETCONFIG " + JSON.stringify(config)); 
    }
    catch (err) {
        if (err instanceof LCSerialCommandError) {
            alert("Save failed: " + err.message);
        }
    }
}

function showConnectMask() {
    $("div.connect-mask").show();
    $("button#connect-button").show();
    $("p#connection-status").hide();
}

function hideConnectMask() {
    $("div.connect-mask").hide();
}

function showConnectionStatus(msg) {
    $("button#connect-button").hide();
    $("p#connection-status").show().text(msg);
}


$(() => {
    if (!("serial" in navigator)) {
        $("body").addClass("not-supported");
    }

    const button = document.getElementById("connect-button");
    button.addEventListener('click', () => {
        navigator.serial.requestPort({filters: [ {usbVendorId: 0x2e8a} ]}).then((port) => {
            lcSerial = new LCSerial(port);
            lcSerial.open(() => {
                lcSerial = null;
                showConnectMask();
            })
                .then(() => { 
                    showConnectionStatus("Connecting...");
                    return lcSerial.doCommand("MENUSPEC") 
                })
                .then(async (menuSpecJSON) => {
                    showConnectionStatus("Fetching config...");
                    console.log("Menu Spec:" + menuSpecJSON);
                    var controls = await buildConfigMenu(JSON.parse(menuSpecJSON));
                    var data = await lcSerial.doCommand("DUMPCONFIG");
                    config = JSON.parse(data);

                    loadConfigValues(controls, config);
                    selectFirstSection();

                    var version = await lcSerial.doCommand("VERSION");
                    var board = "";
                    try {
                        // not supported on old boards
                        board = await lcSerial.doCommand("BOARD");
                    }
                    catch {
                    }
                    $("div.version").text(board + " " + version);

                    hideConnectMask();

                    const container = $("div#buttons");
                    container.empty();
                    /*
                    config.lights.forEach((light, index) => {
                        $("div")
                            .append(
                                $("<button>")
                                    .text("Flash " + index)
                                    .on("click", () => lcSerial.doCommand("IDENT " + index))
                                )
                            .appendTo(container);
                    });
                    */
                });
        }).catch((e) => {
          // The user didn't select a port.
        });
    });

    /*
    document.getElementById("save-button").addEventListener('click', async () => {
        $("div.button-mask").addClass("active").find(".save-status").text("Saving...");
        await saveConfig();
        $("div.button-mask").removeClass("active");
    });
    */

    document.getElementById("close-button").addEventListener('click', async () => {
        if (lcSerial !== null) {
            await lcSerial.close()
            lcSerial = null;
        }
        showConnectMask();
    });

    /*
    buildConfigMenu(menuspec);
    hideConnectMask();
    selectFirstSection();
    */

});
