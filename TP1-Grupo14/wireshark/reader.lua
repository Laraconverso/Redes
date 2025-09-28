--[[
    Plugin de Wireshark para analizar los paquetes enviados.

    RDT Protocol Data
    ├── Segment Number (seg_num)
    ├── Acknowledgment Number (ack_num)
    ├── Flags (flags)
    │    ├── UPL (flag_upl)
    │    ├── DWL (flag_dwl)
    │    ├── ACK (flag_ack)
    │    ├── FIN (flag_fin)
    │    └── PROTO (flag_proto)
    ├── Payload Length (payload_len)
    └── Payload (payload)
    
]]

local protocol = Proto("rdt_proto", "Grupo 14 - RDT Protocol")

local seg_num = ProtoField.uint32("rdt_proto.seg_num", "Segment Number", base.DEC)
local ack_num = ProtoField.uint32("rdt_proto.ack_num", "Acknowledgment Number", base.DEC)

local flags = ProtoField.uint8("rdt_proto.flags", "Flags", base.HEX)
local flag_upl = ProtoField.bool("rdt_proto.flags.upl", "UPL", 8, nil, 0x80)
local flag_dwl = ProtoField.bool("rdt_proto.flags.dwl", "DWL", 8, nil, 0x40)
local flag_ack = ProtoField.bool("rdt_proto.flags.ack", "ACK", 8, nil, 0x20)
local flag_fin = ProtoField.bool("rdt_proto.flags.fin", "FIN", 8, nil, 0x10)
local flag_proto = ProtoField.uint8("rdt_proto.flags.proto", "PROTO", base.DEC, nil, 0x0F)

local payload_len = ProtoField.uint16("rdt_proto.payload_len", "Payload Length", base.DEC)
local payload = ProtoField.bytes("rdt_proto.payload", "Payload")

protocol.fields = {
    seg_num, ack_num,
    flags, flag_upl, flag_dwl, flag_ack, flag_fin, flag_proto,
    payload_len, payload }

-- Función para iniciar la dissección de los paquetes
-- @param buffer Bytes a leer
-- @param pinfo Guarda la información del protocolo
-- @param tree Árbol de la dissección usado para mostrar la información
function protocol.dissector(buffer, pinfo, tree)
    if buffer:len() < 11 then
        return
    end
    pinfo.cols.protocol = protocol.name

    local subtree = tree:add(protocol, buffer(), "RDT Protocol Data")

    subtree:add(seg_num, buffer(0, 4))
    subtree:add(ack_num, buffer(4, 4))

    local flag_buffer = buffer(8, 1)
    -- Armado de los flags como subrama
    local flag_tree = subtree:add(flags, flag_buffer)
    flag_tree:add(flag_upl, flag_buffer)
    flag_tree:add(flag_dwl, flag_buffer)
    flag_tree:add(flag_ack, flag_buffer)
    flag_tree:add(flag_fin, flag_buffer)

    local proto_value = bit.band(flag_buffer:uint(), 0x0F)
    flag_tree:add(buffer(8, 1), string.format("PROTO: %d", proto_value))

    subtree:add(payload_len, buffer(9, 2))
    subtree:add(payload, buffer(11))
end

local udp_port = DissectorTable.get("udp.port")
udp_port:add(12345, protocol) -- Cambiar número de puerto por el usado
