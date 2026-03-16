from src.ta import setup, keygen
from src.scheme import encrypt
from src.rsu import rsu_transform
from src.obu import final_decrypt
from src.types import PolicyNotSatisfiedError, RevocationState


def test_valid_user_can_decrypt():
    pp, msk = setup()
    bundle = keygen(
        pp,
        msk,
        uid='veh-001',
        static_attrs=['role:ambulance', 'dept:traffic'],
        dynamic_attrs=['region:r1', 'timeslot:t1'],
    )
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r1', 'timeslot:t1'],
    )
    transformed = rsu_transform(
        pp,
        bundle.certificate,
        bundle.transform_key,
        ciphertext,
        RevocationState(),
        context={'region:r1', 'timeslot:t1'},
    )
    plaintext = final_decrypt(pp, bundle.final_key, transformed)
    assert plaintext == b'hello-iov'


def test_dynamic_policy_mismatch_fails():
    pp, msk = setup()
    bundle = keygen(
        pp,
        msk,
        uid='veh-002',
        static_attrs=['role:ambulance', 'dept:traffic'],
        dynamic_attrs=['region:r1', 'timeslot:t1'],
    )
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r2', 'timeslot:t1'],
    )
    try:
        rsu_transform(
            pp,
            bundle.certificate,
            bundle.transform_key,
            ciphertext,
            RevocationState(),
            context={'region:r1', 'timeslot:t1'},
        )
    except PolicyNotSatisfiedError:
        return
    raise AssertionError('expected dynamic policy mismatch to fail')


def test_static_policy_mismatch_fails():
    pp, msk = setup()
    bundle = keygen(
        pp,
        msk,
        uid='veh-003',
        static_attrs=['role:ambulance'],
        dynamic_attrs=['region:r1', 'timeslot:t1'],
    )
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r1', 'timeslot:t1'],
    )
    try:
        rsu_transform(
            pp,
            bundle.certificate,
            bundle.transform_key,
            ciphertext,
            RevocationState(),
            context={'region:r1', 'timeslot:t1'},
        )
    except PolicyNotSatisfiedError:
        return
    raise AssertionError('expected static policy mismatch to fail')
