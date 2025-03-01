# Basic Explanation of the Slack Bot

## Role of the Bot
The bot operates in a specific Slack channel and provides the following functionalities:

- **Remote Control of the STM Controller**  
  Specifically, it interacts with `LabviewRemoteManager` by getting and setting variables defined in `LabviewRemoteManager.RemoteDataType`.

- **Natural Language Conversation Feature**  
  The bot can engage in casual conversation using a natural language engine (e.g., to provide companionship for researchers during holidays like Christmas).

## Types of Messages Posted in Slack
Users can post two types of messages in the channel:  
- **Conversation Messages**: Regular messages that do not require any special formatting.  
- **Remote Command Messages**: These must be formatted as follows:

`command_type@@@variable`



If a message contains `@@@`, it is recognized as a remote command.

## Bot Reactions
In the designated Slack channel, the bot reacts to user messages with specific emojis:

- :eyes: – Similar to the "read" indicator in LINE. If this reaction is missing, the bot is either offline or the user ID is banned.  
- :two_hearts: – The bot recognized and processed the message as a conversation.  
- :sparkles: – The bot recognized and processed the message as a remote command.  
- :broken_heart: – The bot attempted to process the message as a remote command but encountered an error.  

---

## Remote Commands

As mentioned earlier, remote command messages follow this format:


`command_type@@@variable`



Each command consists of `command_type` and `variable`.  
Line breaks in messages are ignored, so commands must be sent one per line.  
Currently, the available `command_type` options are:

| Command Type | Function |
|-------------|----------|
| `get`  | Retrieves a variable |
| `set`  | Modifies a variable |
| `file` | Sends a `.pkl` file |
| `help` | Lists available variables |

### 1. Get Command


```
get@@@varname
```


`varname` corresponds to a member variable within `LabviewRemoteManager.RemoteDataType` or its related classes.  
For example:  


`get@@@PythonScanParam`



returns all member variables of the `PythonScanParam` class.  

If a specific variable within `PythonScanParam` exists, such as `Aux2ScanSize`, the following command:




`get@@@Aux2ScanSize`


returns only that variable.

---

### 2. Set Command

```
set@@@varname=value
set@@@varname=json_str 
```


For example:  

`set@@@PythonScanParam={"Aux1ScanSize"=256, "Aux2ScanSize"=256}`

`set@@@Aux2ScanSize=256`


For **structured classes** (`PythonScanParam`, `StageConfigure`, `ScanDataHeader`), values should be provided as a JSON string to modify specific variables.  
For **individual variables**, use the `var_name=value` format.

---

### 3. File Command

```
file@@@path_to_file
```

`file@@@E:\LabviewProject\Labview-SPMController\python\smart_spm\Datas\001_20220114_test`



Specify the **file path without an extension**.  
The file, along with scan results, will be posted in Slack once scanning is complete. You can copy the file path from there.

---

### 4. Help Command

```
help@@@
```



This dynamically retrieves and lists available variables.  
Unlike the variable list in this document, which requires manual updates, the `help` command always reflects the latest variable set.

---

## List of Variables

### Variables in `LabviewRemoteManager.RemoteDataType`

| Variable Type | Description |
|--------------|------------|
| `PythonScanParam` | Structured Class |
| `StageConfigure` | Structured Class |
| `ScanDataHeader` | Structured Class |
| `DriftX` | Drift in X direction (V/s) |
| `DriftY` | Drift in Y direction (V/s) |
| `DriftZ` | Drift in Z direction (V/s) |
| `DriftX_ADD` | Additional drift in X direction (V/s) |
| `DriftY_ADD` | Additional drift in Y direction (V/s) |
| `DriftZ_ADD` | Additional drift in Z direction (V/s) |
| `ScanEnabled` | Scan start button |
| `StageOffset_X_Tube` | Tube Scanner X-axis offset (V) |
| `StageOffset_Y_Tube` | Tube Scanner Y-axis offset (V) |
| `StageOffset_X_HS` | High-Speed Scanner X-axis offset (V) |
| `StageOffset_Y_HS` | High-Speed Scanner Y-axis offset (V) |
| `Go_Home` | Moves Z to the home position using the Unisoku Stage Controller |

### [Variables in Structured Classes](https://github.com/DIAOZHUO/SPMUtil/blob/main/SPMUtil/structures/scan_data_format.py)

| Variable Type | Description |
|--------------|------------|
| `Sample_Bias` |  |
| `Tube_Scanner_Offset_X` |  |
| `Tube_Scanner_Offset_Y` |  |
| `High_Speed_Scanner_Offset_X` |  |
| `High_Speed_Scanner_Offset_Y` |  |
| `Scan_Speed` |  |
| `XY_Scan_Option` |  |
| `Z_Scan_Option` |  |
| `Aux1Pingpong` |  |
| `Aux2Pingpong` |  |
| `ZRotation` |  |
| `Aux1MinVoltage` |  |
| `Aux1MaxVoltage` |  |
| `Aux2MinVoltage` |  |
| `Aux2MaxVoltage` |  |
| `Aux1ScanSize` |  |
| `Aux2ScanSize` |  |
| `Aux1Type` |  |
| `Aux2Type` |  |
| `Xtilt` |  |
| `Ytilt` |  |
| `Applytilt` |  |
| `Date` |  |
| `Time_Start_Scan` |  |
| `Time_End_Scan` |  |
| `Scan_Method` |  |

This document provides an overview of the Slack bot functionalities, command structures, and available variables for remote control.

