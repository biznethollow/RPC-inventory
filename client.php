<?php

// ==================================================
// FUNCTION XML-RPC CLIENT
// ==================================================
function rpc_call($method, $params = [])
{
    // Membuat XML-RPC request
    $xml = '<?xml version="1.0"?>';
    $xml .= '<methodCall>';
    $xml .= '<methodName>' . htmlspecialchars($method) . '</methodName>';
    $xml .= '<params>';

    foreach ($params as $param) {
        $xml .= '<param>';
        $xml .= '<value>';

        if (is_int($param)) {
            $xml .= '<int>' . $param . '</int>';
        } else {
            $xml .= '<string>';
            $xml .= htmlspecialchars($param);
            $xml .= '</string>';
        }

        $xml .= '</value>';
        $xml .= '</param>';
    }

    $xml .= '</params>';
    $xml .= '</methodCall>';

    // ==================================================
    // MENGIRIM REQUEST KE PYTHON
    // ==================================================
    $context = stream_context_create([
        'http' => [
            'method'  => 'POST',
            'header'  => "Content-Type: text/xml\r\n" .
                         "Content-Length: " . strlen($xml) . "\r\n",
            'content' => $xml,
            'timeout' => 10
        ]
    ]);

    $response = @file_get_contents(
        'http://localhost:8000',
        false,
        $context
    );

    // Jika server Python tidak dapat dihubungi
    if ($response === false) {
        return [
            'error'   => true,
            'message' => 'Tidak dapat terhubung ke server Python'
        ];
    }

    return parse_xmlrpc_response($response);
}


// ==================================================
// PARSE XML-RPC RESPONSE
// ==================================================
function parse_xmlrpc_response($xml)
{
    $simpleXml = simplexml_load_string($xml);

    if ($simpleXml === false) {
        return [
            'error'   => true,
            'message' => 'Response XML tidak valid'
        ];
    }

    // Cek RPC Fault
    if (isset($simpleXml->fault)) {
        return [
            'error'   => true,
            'message' => 'RPC Fault dari server Python'
        ];
    }

    $value = $simpleXml->params->param->value;

    return parse_xmlrpc_value($value);
}


// ==================================================
// PARSE XML-RPC VALUE
// ==================================================
function parse_xmlrpc_value($value)
{
    // STRING
    if (isset($value->string)) {
        return (string) $value->string;
    }

    // INTEGER
    if (isset($value->int)) {
        return (int) $value->int;
    }

    // BOOLEAN
    if (isset($value->boolean)) {
        return ((int) $value->boolean) === 1;
    }

    // ARRAY
    if (isset($value->array)) {
        $result = [];

        foreach ($value->array->data->value as $item) {
            $result[] = parse_xmlrpc_value($item);
        }

        return $result;
    }

    // STRUCT
    if (isset($value->struct)) {
        $result = [];

        foreach ($value->struct->member as $member) {
            $name = (string) $member->name;

            $result[$name] = parse_xmlrpc_value(
                $member->value
            );
        }

        return $result;
    }

    return null;
}


// ==================================================
// VARIABLE PESAN
// ==================================================
$message = null;
$message_type = 'success';


// ==================================================
// TAMBAH BARANG
// ==================================================
if (isset($_POST['add'])) {

    $name = trim($_POST['name']);
    $quantity = intval($_POST['quantity']);

    $result = rpc_call(
        'add_item',
        [$name, $quantity]
    );

    if (isset($result['error']) && $result['error']) {

        $message = $result['message'];
        $message_type = 'error';

    } elseif (isset($result['success'])) {

        $message = $result['message'];
        $message_type = $result['success']
            ? 'success'
            : 'error';
    }
}


// ==================================================
// AMBIL SEBAGIAN BARANG
// ==================================================
if (isset($_POST['take'])) {

    $name = trim($_POST['name']);
    $quantity = intval($_POST['quantity']);

    $result = rpc_call(
        'take_item',
        [$name, $quantity]
    );

    if (isset($result['error']) && $result['error']) {

        $message = $result['message'];
        $message_type = 'error';

    } elseif (isset($result['success'])) {

        $message = $result['message'];
        $message_type = $result['success']
            ? 'success'
            : 'error';
    }
}


// ==================================================
// HAPUS BARANG
// ==================================================
if (isset($_POST['delete'])) {

    $name = $_POST['delete'];

    $result = rpc_call(
        'delete_item',
        [$name]
    );

    if (isset($result['error']) && $result['error']) {

        $message = $result['message'];
        $message_type = 'error';

    } elseif (isset($result['success'])) {

        $message = $result['message'];
        $message_type = $result['success']
            ? 'success'
            : 'error';
    }
}


// ==================================================
// AMBIL SEMUA BARANG
// ==================================================
$items = rpc_call('get_items');


// Jika terjadi error ketika mengambil barang
if (
    is_array($items) &&
    isset($items['error']) &&
    $items['error']
) {

    if ($message === null) {
        $message = $items['message'];
        $message_type = 'error';
    }

    $items = [];
}

?>

<!DOCTYPE html>
<html lang="id">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Inventory XML-RPC</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 40px;
        }

        .container {
            max-width: 900px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
        }

        h2 {
            margin-top: 30px;
        }

        .form-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        input {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        input[type="text"] {
            flex: 1;
        }

        input[type="number"] {
            width: 150px;
        }

        button {
            padding: 10px 15px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
        }

        .add {
            background: #2ecc71;
            color: white;
        }

        .take {
            background: #f39c12;
            color: white;
        }

        .delete {
            background: #e74c3c;
            color: white;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th,
        td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }

        th {
            background: #eee;
        }

        .action-form {
            display: flex;
            gap: 5px;
            margin: 0;
        }

        .action-form input {
            width: 80px;
        }

        .message {
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 5px;
        }

        .success-message {
            background: #d4edda;
            color: #155724;
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
        }

    </style>

</head>

<body>

<div class="container">

    <h1>
        Inventory Barang XML-RPC
    </h1>


    <!-- ========================================= -->
    <!-- PESAN -->
    <!-- ========================================= -->

    <?php if ($message !== null): ?>

        <div class="message
            <?= $message_type === 'success'
                ? 'success-message'
                : 'error-message'
            ?>">

            <?= htmlspecialchars($message) ?>

        </div>

    <?php endif; ?>


    <!-- ========================================= -->
    <!-- TAMBAH BARANG -->
    <!-- ========================================= -->

    <h2>
        Tambah Barang
    </h2>

    <form method="POST">

        <div class="form-group">

            <input
                type="text"
                name="name"
                placeholder="Nama barang"
                required
            >

            <input
                type="number"
                name="quantity"
                placeholder="Jumlah"
                min="1"
                required
            >

            <button
                type="submit"
                name="add"
                class="add"
            >
                Tambah
            </button>

        </div>

    </form>


    <!-- ========================================= -->
    <!-- DAFTAR BARANG -->
    <!-- ========================================= -->

    <h2>
        Daftar Barang
    </h2>

    <table>

        <tr>

            <th>No</th>
            <th>Nama Barang</th>
            <th>Stok</th>
            <th>Aksi</th>

        </tr>


        <?php if (is_array($items) && count($items) > 0): ?>

            <?php $no = 1; ?>

            <?php foreach ($items as $item): ?>

                <tr>

                    <td>
                        <?= $no++ ?>
                    </td>

                    <td>
                        <?= htmlspecialchars($item['name']) ?>
                    </td>

                    <td>
                        <?= $item['quantity'] ?>
                    </td>

                    <td>

                        <!-- ================================= -->
                        <!-- FORM AMBIL SEBAGIAN -->
                        <!-- ================================= -->

                        <form
                            method="POST"
                            class="action-form"
                        >

                            <input
                                type="hidden"
                                name="name"
                                value="<?= htmlspecialchars($item['name']) ?>"
                            >

                            <input
                                type="number"
                                name="quantity"
                                placeholder="Jumlah"
                                min="1"
                                max="<?= $item['quantity'] ?>"
                                required
                            >

                            <button
                                type="submit"
                                name="take"
                                class="take"
                            >
                                Ambil
                            </button>

                        </form>


                        <br>


                        <!-- ================================= -->
                        <!-- FORM HAPUS -->
                        <!-- ================================= -->

                        <form method="POST">

                            <button
                                type="submit"
                                name="delete"
                                value="<?= htmlspecialchars($item['name']) ?>"
                                class="delete"
                                onclick="return confirm(
                                    'Yakin ingin menghapus barang ini?'
                                )"
                            >
                                Hapus
                            </button>

                        </form>

                    </td>

                </tr>

            <?php endforeach; ?>

        <?php else: ?>

            <tr>

                <td
                    colspan="4"
                    style="text-align: center;"
                >
                    Belum ada barang
                </td>

            </tr>

        <?php endif; ?>

    </table>

</div>

</body>

</html>