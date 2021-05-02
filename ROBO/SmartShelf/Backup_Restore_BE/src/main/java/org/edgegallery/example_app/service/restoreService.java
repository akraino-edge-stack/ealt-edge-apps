package org.edgegallery.example_app.service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.StringTokenizer;

import org.apache.commons.lang.StringUtils;
import org.edgegallery.example_app.common.Constants;
import org.edgegallery.example_app.model.EALTEdgeBackup;
import org.edgegallery.example_app.model.EALTEdgeRestore;
import org.edgegallery.example_app.util.ShellCommand;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class restoreService {

    @Autowired
    ShellCommand shellCommand;

    public String create_restore(String restorename, String backupname) {
        String ip = System.getenv("HOSTIP");
        String port = System.getenv("SSHPORT");

        String command = "sshpass ssh -p " + port + " root@" + ip + " velero restore create " + restorename + " --from-backup " +
                         backupname;

        System.out.println(command);

        String output = shellCommand.executeCommand(command);

        System.out.println(output);
        return "success";
    }
    
    /**
     * get restore table and parse
     * @return
     */
    public List<EALTEdgeRestore> getRestoreTables() {
        String ip = System.getenv("HOSTIP");
        String port = System.getenv("SSHPORT");

        String command = "sshpass ssh -p " + port + " root@" + ip + " velero get restores";

        System.out.println(command);

        List<EALTEdgeRestore> restoresList = new ArrayList<EALTEdgeRestore>();
        restoresList = shellCommand.executeRestoreCommand(command);

        return restoresList;
    }
}
