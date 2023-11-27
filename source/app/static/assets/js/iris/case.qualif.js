sections = ["orga","desc","proc","arch"];
var edit_mode = false;

function load_qualif_data(){
    /* Loads qualif data and inserts it
    in corresponding div
    */
    post_request_api('/case/qualif/get', JSON.stringify(data), true)
    .done((data) => {
        qualif_info = data.data["qualifinfo"];
        sections = ["orga","desc","proc","arch"];
        sections.forEach(function(section){
            var editor = ace.edit("editor_qualif_"+section,
            {
                autoScrollEditorIntoView: true,
                minLines: 4
            });
            editor.getSession().setValue(qualif_info[section]);
            div_id="#targetDiv_"+section;
            $(div_id).html(qualif_info[section]);
        })

        checklist_info = data.data["checklist_info"];
        Object.keys(checklist_info).forEach(inpt => {
            var chck = checklist_info[inpt];
            $("#"+inpt).prop("checked", chck);
        });
    });
}

function edit_qualif_summaries() {
    /* Sets page in edition mode */
    if(edit_mode) {
        edit_mode = false;
        $('#last_saved').text('Syncing..').addClass('badge-danger').removeClass('badge-success');
        data = {};
        data["qualifinfo"] = {
            "orga":editor_orga.getSession().getValue(),
            "desc":editor_desc.getSession().getValue(),
            "proc":editor_proc.getSession().getValue(),
            "arch":editor_arch.getSession().getValue(),
        }
        data["checklist_info"] = build_json_checklist();
        
        post_request_api('/case/qualif/refresh', JSON.stringify(data), true)
        .done((data) => {
            sections.forEach(function(section){
                container_id = "#container_editor_qualif_"+section;
                btn_id = "#container_editor_qualif_"+section+"_edition_btn";
                div_id = "#targetDiv_"+section;
                var editor = ace.edit("editor_qualif_"+section,
                {
                    autoScrollEditorIntoView: true,
                    minLines: 4
                });
                editor.getSession().setValue(data.data[section]);
                div_id="#targetDiv_"+section;

                $(container_id).toggle();
                $(btn_id).hide();
                $(div_id).html(data.data[section]);
                $(div_id).show(100);
            })
            $("#editbtn").html('Edit');
            $('#last_saved').text('Saved').addClass('badge-success').removeClass('badge-danger');
        });
    }
    else {
        sections.forEach(function(section){
            container_id = "#container_editor_qualif_"+section;
            btn_id = "#container_editor_qualif_"+section+"_edition_btn";
            div_id = "#targetDiv_"+section;
            $(container_id).toggle();
            $(btn_id).show(100);
            $(div_id).hide();
        })
        $("#editbtn").html('Save');
        edit_mode = true;
    }
}

var editor_orga = ace.edit("editor_qualif_orga",
    {
        autoScrollEditorIntoView: true,
        minLines: 4
    });
var editor_desc = ace.edit("editor_qualif_desc",
{
    autoScrollEditorIntoView: true,
    minLines: 4
});
var editor_proc = ace.edit("editor_qualif_proc",
    {
        autoScrollEditorIntoView: true,
        minLines: 4
    });
var editor_arch = ace.edit("editor_qualif_arch",
{
    autoScrollEditorIntoView: true,
    minLines: 4
});

function save_editors(){
    /*
    Saves qualif data to db
    */
    $('#last_saved').text('Syncing..').addClass('badge-danger').removeClass('badge-success');
    data = {};
    data["qualifinfo"] = {
        "orga":editor_orga.getSession().getValue(),
        "desc":editor_desc.getSession().getValue(),
        "proc":editor_proc.getSession().getValue(),
        "arch":editor_arch.getSession().getValue(),
    }
    data["checklist_info"] = build_json_checklist();

    post_request_api('/case/qualif/save', JSON.stringify(data), true)
    .done((data) => {
        $('#last_saved').text('Saved').addClass('badge-success').removeClass('badge-danger');
    });
}

function export_checklist(button) {
    var data_checklist = build_json_checklist();
    const dataJSON = JSON.stringify(data_checklist);
    var data = "text/json;charset=utf-8," + dataJSON;
    console.log(dataJSON);
    button.setAttribute("href","data:"+data);
    button.setAttribute("download", "data.json");

    return dataJSON;
}

function build_json_checklist(){
    var forms_qualif = $(".form_qualif :input");
    result = {}
    for(i=0;i<forms_qualif.length;i++) {
        var id = forms_qualif[i].id;
        var checked = forms_qualif[i].checked;
        result[id] = checked;
    }
    return result;
}

$(document).ready(function(){
    load_qualif_data();

    editors = ["editor_qualif_orga",
        "editor_qualif_desc",
        "editor_qualif_proc",
        "editor_qualif_arch"]
    editors.forEach(function(editor_id){
        var editor = ace.edit(editor_id,
        {
            autoScrollEditorIntoView: true,
            minLines: 4
        });

        if ($("#editor_qualif_desc").attr("data-theme") != "dark") {
            editor.setTheme("ace/theme/tomorrow");
        } else {
            editor.setTheme("ace/theme/tomorrow_night");
        }
        editor.session.setMode("ace/mode/markdown");
        editor.renderer.setShowGutter(true);
        editor.setOption("showLineNumbers", true);
        editor.setOption("showPrintMargin", false);
        editor.setOption("displayIndentGuides", true);
        editor.setOption("indentedSoftWrap", false);
        editor.session.setUseWrapMode(true);
        editor.setOption("maxLines", "Infinity")
        editor.renderer.setScrollMargin(8, 5)
        editor.setOption("enableBasicAutocompletion", true);
        editor.commands.addCommand({
            name: 'save',
            bindKey: {win: "Ctrl-S", "mac": "Cmd-S"},
            exec: function(editor) {
                save_editors(false);
            }
        });
    })

    
});